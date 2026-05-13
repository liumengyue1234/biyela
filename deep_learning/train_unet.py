"""
CT图像松材线虫病检测系统 - 改进U-Net训练脚本
实现分阶段训练策略:
- 第一阶段: 采用预训练权重，学习率1e-4，快速收敛
- 第二阶段: 冻结编码端前3层，仅训练解码端与注意力模块，学习率1e-5
"""
import os
import sys
import time
import json
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from models.improved_unet import ImprovedUNet, StandardUNet
from models.losses import CombinedLoss, DiceLoss
from data.dataset import build_dataloaders, prepare_dataset
from utils.metrics import evaluate_segmentation


class Trainer:
    """改进U-Net训练器"""

    def __init__(self, model, train_loader, val_loader, config, device,
                 checkpoint_dir='checkpoints', results_dir='results'):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config
        self.device = device
        self.checkpoint_dir = checkpoint_dir
        self.results_dir = results_dir

        os.makedirs(checkpoint_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)

        # 损失函数
        self.criterion = CombinedLoss(
            dice_weight=config.get('dice_weight', 0.5),
            ce_weight=config.get('ce_weight', 0.5)
        )

        # 优化器
        self.optimizer = AdamW(
            model.parameters(),
            lr=config.get('lr_phase1', 1e-4),
            weight_decay=config.get('weight_decay', 1e-4)
        )

        # 学习率调度器
        self.scheduler = CosineAnnealingLR(
            self.optimizer,
            T_max=config.get('epochs_phase1', 50),
            eta_min=1e-7
        )

        # 记录
        self.train_losses = []
        self.val_losses = []
        self.val_dices = []
        self.best_dice = 0.0
        self.patience_counter = 0

    def train_epoch(self, epoch):
        """训练一个epoch"""
        self.model.train()
        total_loss = 0.0
        dice_losses = []
        ce_losses = []

        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch + 1}')
        for batch_idx, (images, masks, _) in enumerate(pbar):
            images = images.to(self.device)
            masks = masks.to(self.device)

            self.optimizer.zero_grad()

            # 前向传播
            outputs = self.model(images)

            # 计算损失
            loss, loss_dict = self.criterion(outputs, masks)

            # 反向传播
            loss.backward()

            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

            self.optimizer.step()

            total_loss += loss.item()
            dice_losses.append(loss_dict['dice_loss'])
            ce_losses.append(loss_dict['ce_loss'])

            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'dice': f'{loss_dict["dice_loss"]:.4f}',
                'ce': f'{loss_dict["ce_loss"]:.4f}'
            })

        avg_loss = total_loss / len(self.train_loader)
        avg_dice = np.mean(dice_losses)
        avg_ce = np.mean(ce_losses)

        return avg_loss, avg_dice, avg_ce

    @torch.no_grad()
    def validate(self, epoch):
        """验证"""
        self.model.eval()
        total_loss = 0.0
        all_metrics = []

        for images, masks, _ in tqdm(self.val_loader, desc='Validating'):
            images = images.to(self.device)
            masks = masks.to(self.device)

            outputs = self.model(images)
            loss, _ = self.criterion(outputs, masks)
            total_loss += loss.item()

            # 计算评估指标
            preds = torch.argmax(outputs, dim=1)
            for pred, mask in zip(preds, masks):
                metrics = evaluate_segmentation(pred.cpu().numpy(), mask.cpu().numpy())
                all_metrics.append(metrics)

        avg_loss = total_loss / len(self.val_loader)

        # 汇总指标
        avg_dice = np.mean([m.get('class1', {}).get('dice', 0) for m in all_metrics])
        avg_iou = np.mean([m.get('class1', {}).get('iou', 0) for m in all_metrics])
        avg_precision = np.mean([m.get('class1', {}).get('precision', 0) for m in all_metrics])
        avg_recall = np.mean([m.get('class1', {}).get('recall', 0) for m in all_metrics])

        print(f'\n验证 - Loss: {avg_loss:.4f}, Dice: {avg_dice:.4f}, '
              f'IoU: {avg_iou:.4f}, Precision: {avg_precision:.4f}, Recall: {avg_recall:.4f}')

        return avg_loss, avg_dice, {
            'dice': avg_dice, 'iou': avg_iou,
            'precision': avg_precision, 'recall': avg_recall
        }

    def save_checkpoint(self, epoch, dice, is_best=False):
        """保存检查点"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'dice': dice,
            'config': self.config,
        }
        path = os.path.join(self.checkpoint_dir, f'checkpoint_epoch_{epoch + 1}.pth')
        torch.save(checkpoint, path)

        if is_best:
            best_path = os.path.join(self.checkpoint_dir, 'best_model.pth')
            torch.save(checkpoint, best_path)
            print(f'  ** 最佳模型已保存! Dice: {dice:.4f} **')

    def freeze_encoder(self, num_layers=3):
        """冻结编码端前N层"""
        print(f'\n冻结编码端前 {num_layers} 层...')
        for name, param in self.model.named_parameters():
            # 冻结encoder1, encoder2, encoder3
            for i in range(1, num_layers + 1):
                if f'encoder{i}' in name:
                    param.requires_grad = False
                    break

        trainable = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total = sum(p.numel() for p in self.model.parameters())
        print(f'可训练参数: {trainable:,} / {total:,} ({100 * trainable / total:.1f}%)')

    def train_phase1(self, epochs=None):
        """
        第一阶段训练: 预训练权重，学习率1e-4，快速收敛
        """
        epochs = epochs or self.config.get('epochs_phase1', 50)
        print("\n" + "=" * 60)
        print("第一阶段训练 - 快速收敛")
        print(f"学习率: {self.config.get('lr_phase1', 1e-4)}")
        print(f"训练轮数: {epochs}")
        print("=" * 60)

        for epoch in range(epochs):
            train_loss, dice_loss, ce_loss = self.train_epoch(epoch)
            val_loss, val_dice, val_metrics = self.validate(epoch)

            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.val_dices.append(val_dice)

            self.scheduler.step()

            # 保存检查点
            is_best = val_dice > self.best_dice
            if is_best:
                self.best_dice = val_dice
                self.patience_counter = 0
            else:
                self.patience_counter += 1

            self.save_checkpoint(epoch, val_dice, is_best)

            # 早停
            if self.patience_counter >= self.config.get('early_stopping_patience', 10):
                print(f'\n早停触发! 连续 {self.patience_counter} 个epoch未提升')
                break

    def train_phase2(self, epochs=None):
        """
        第二阶段训练: 冻结编码端前3层，学习率1e-5，精细优化
        """
        epochs = epochs or self.config.get('epochs_phase2', 30)

        # 加载第一阶段最佳模型
        best_path = os.path.join(self.checkpoint_dir, 'best_model.pth')
        if os.path.exists(best_path):
            checkpoint = torch.load(best_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            print(f'加载第一阶段最佳模型, Dice: {checkpoint["dice"]:.4f}')

        # 冻结编码端
        self.freeze_encoder(self.config.get('freeze_encoder_layers', 3))

        # 调整学习率
        lr = self.config.get('lr_phase2', 1e-5)
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr

        # 重置调度器
        self.scheduler = CosineAnnealingLR(self.optimizer, T_max=epochs, eta_min=1e-8)

        print("\n" + "=" * 60)
        print("第二阶段训练 - 精细优化")
        print(f"学习率: {lr}")
        print(f"训练轮数: {epochs}")
        print("=" * 60)

        self.patience_counter = 0
        for epoch in range(epochs):
            train_loss, dice_loss, ce_loss = self.train_epoch(epoch)
            val_loss, val_dice, val_metrics = self.validate(epoch)

            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.val_dices.append(val_dice)

            self.scheduler.step()

            is_best = val_dice > self.best_dice
            if is_best:
                self.best_dice = val_dice
                self.patience_counter = 0
            else:
                self.patience_counter += 1

            self.save_checkpoint(epoch + 1000, val_dice, is_best)  # 加偏移区分阶段

            if self.patience_counter >= self.config.get('early_stopping_patience', 10):
                print(f'\n早停触发!')
                break

    def train(self):
        """完整两阶段训练流程"""
        self.train_phase1()
        self.train_phase2()
        self.plot_training_curves()
        return self.best_dice

    def plot_training_curves(self):
        """绘制训练曲线"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        # 损失曲线
        axes[0].plot(self.train_losses, label='训练损失', color='blue')
        axes[0].plot(self.val_losses, label='验证损失', color='red')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('训练/验证损失曲线')
        axes[0].legend()
        axes[0].grid(True)

        # Dice曲线
        axes[1].plot(self.val_dices, label='验证Dice系数', color='green')
        axes[1].axhline(y=self.best_dice, color='r', linestyle='--',
                        label=f'最佳Dice: {self.best_dice:.4f}')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Dice')
        axes[1].set_title('Dice系数变化曲线')
        axes[1].legend()
        axes[1].grid(True)

        # 两阶段分界线
        if len(self.train_losses) > 0:
            phase1_len = self.config.get('epochs_phase1', 50)
            for ax in axes[:2]:
                ax.axvline(x=phase1_len, color='gray', linestyle=':',
                          label='阶段分界')

        # 学习率曲线（简化）
        axes[2].text(0.5, 0.5, f'最佳Dice: {self.best_dice:.4f}\n'
                               f'最终训练损失: {self.train_losses[-1]:.4f}\n'
                               f'最终验证损失: {self.val_losses[-1]:.4f}',
                    transform=axes[2].transAxes, fontsize=14,
                    ha='center', va='center',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        axes[2].set_title('训练摘要')

        plt.tight_layout()
        save_path = os.path.join(self.results_dir, 'training_curves.png')
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'训练曲线已保存: {save_path}')


@torch.no_grad()
def test_model(model, test_loader, device, results_dir='results'):
    """测试模型并生成评估报告"""
    os.makedirs(results_dir, exist_ok=True)
    model.eval()

    all_metrics = []
    all_images = []

    for images, masks, names in tqdm(test_loader, desc='Testing'):
        images = images.to(device)
        masks = masks.to(device)

        outputs = model(images)
        preds = torch.argmax(outputs, dim=1)

        for i in range(images.shape[0]):
            pred = preds[i].cpu().numpy()
            mask = masks[i].cpu().numpy()
            metrics = evaluate_segmentation(pred, mask)
            metrics['image_name'] = names[i] if isinstance(names, list) else names
            all_metrics.append(metrics)

            # 保存可视化结果
            image_np = images[i].cpu().permute(1, 2, 0).numpy()
            image_np = (image_np * np.array([0.229, 0.224, 0.225]) +
                       np.array([0.485, 0.456, 0.406])) * 255
            image_np = image_np.astype(np.uint8)

            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            axes[0].imshow(image_np)
            axes[0].set_title('CT图像')
            axes[1].imshow(mask, cmap='gray')
            axes[1].set_title('真实标注')
            axes[2].imshow(pred, cmap='gray')
            axes[2].set_title('模型预测')
            for ax in axes:
                ax.axis('off')
            plt.tight_layout()
            save_name = f'pred_{names[i]}' if isinstance(names, list) else f'pred_{i}.png'
            plt.savefig(os.path.join(results_dir, save_name), dpi=100, bbox_inches='tight')
            plt.close()

    # 汇总指标
    avg_dice = np.mean([m.get('class1', {}).get('dice', 0) for m in all_metrics])
    avg_iou = np.mean([m.get('class1', {}).get('iou', 0) for m in all_metrics])
    avg_precision = np.mean([m.get('class1', {}).get('precision', 0) for m in all_metrics])
    avg_recall = np.mean([m.get('class1', {}).get('recall', 0) for m in all_metrics])
    avg_f1 = np.mean([m.get('class1', {}).get('f1', 0) for m in all_metrics])
    avg_acc = np.mean([m.get('overall_accuracy', 0) for m in all_metrics])

    report = {
        'model': 'ImprovedUNet',
        'test_samples': len(all_metrics),
        'metrics': {
            'dice': float(avg_dice),
            'iou': float(avg_iou),
            'precision': float(avg_precision),
            'recall': float(avg_recall),
            'f1': float(avg_f1),
            'accuracy': float(avg_acc),
        }
    }

    # 保存报告
    report_path = os.path.join(results_dir, 'test_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"Dice系数: {avg_dice:.4f}")
    print(f"IoU: {avg_iou:.4f}")
    print(f"精确率: {avg_precision:.4f}")
    print(f"召回率: {avg_recall:.4f}")
    print(f"F1分数: {avg_f1:.4f}")
    print(f"准确率: {avg_acc:.4f}")
    print(f"报告已保存: {report_path}")

    return report


def main():
    parser = argparse.ArgumentParser(description='改进U-Net训练脚本')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'test', 'prepare'],
                        help='运行模式: train/test/prepare')
    parser.add_argument('--data_dir', type=str, default='../dataset',
                        help='数据集目录')
    parser.add_argument('--checkpoint', type=str, default=None,
                        help='测试时加载的检查点路径')
    parser.add_argument('--batch_size', type=int, default=4)
    parser.add_argument('--epochs_phase1', type=int, default=50)
    parser.add_argument('--epochs_phase2', type=int, default=30)
    args = parser.parse_args()

    # 设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'使用设备: {device}')

    if args.mode == 'prepare':
        # 准备数据集
        source_dirs = [
            r'D:\松材线虫\标注\first',
            r'D:\松材线虫\标注\third',
        ]
        prepare_dataset(source_dirs, os.path.join(PROJECT_ROOT, '..', 'dataset'))
        return

    # 构建数据加载器
    data_dir = os.path.join(PROJECT_ROOT, args.data_dir)
    train_loader, val_loader, test_loader = build_dataloaders(
        data_dir, batch_size=args.batch_size
    )

    # 训练配置
    train_config = {
        'epochs_phase1': args.epochs_phase1,
        'epochs_phase2': args.epochs_phase2,
        'lr_phase1': 1e-4,
        'lr_phase2': 1e-5,
        'weight_decay': 1e-4,
        'dice_weight': 0.5,
        'ce_weight': 0.5,
        'freeze_encoder_layers': 3,
        'early_stopping_patience': 10,
    }

    if args.mode == 'train':
        # 构建模型
        model = ImprovedUNet(
            in_channels=3, out_channels=2, base_filters=64,
            use_cbam=True, use_residual=True, use_multiscale=True
        )
        print(f'模型参数量: {sum(p.numel() for p in model.parameters()):,}')

        # 训练
        checkpoint_dir = os.path.join(PROJECT_ROOT, 'checkpoints', 'improved_unet')
        results_dir = os.path.join(PROJECT_ROOT, 'results', 'improved_unet')

        trainer = Trainer(
            model, train_loader, val_loader,
            train_config, device, checkpoint_dir, results_dir
        )
        best_dice = trainer.train()
        print(f'\n训练完成! 最佳Dice: {best_dice:.4f}')

        # 测试
        best_path = os.path.join(checkpoint_dir, 'best_model.pth')
        if os.path.exists(best_path):
            checkpoint = torch.load(best_path, map_location=device)
            model.load_state_dict(checkpoint['model_state_dict'])
        test_model(model, test_loader, device, os.path.join(results_dir, 'test'))

    elif args.mode == 'test':
        model = ImprovedUNet(in_channels=3, out_channels=2, base_filters=64,
                             use_cbam=True, use_residual=True, use_multiscale=True)
        if args.checkpoint:
            checkpoint = torch.load(args.checkpoint, map_location=device)
            model.load_state_dict(checkpoint['model_state_dict'])
        test_model(model, test_loader, device)


if __name__ == '__main__':
    main()
