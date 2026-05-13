#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化脚本
功能：1) 可视化训练过程中的损失曲线  2) 可视化模型预测结果对比  3) 生成混淆矩阵  4) 可视化注意力热力图
用法：
  python visualize.py --mode training --log-dir ../results/
  python visualize.py --mode prediction --model-path ../weights/improved_unet_best.pth --image-path ../dataset/images/test/
  python visualize.py --mode attention --model-path ../weights/improved_unet_best.pth --image-path ../dataset/images/test/
"""

import argparse
import os
import json
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import cv2
from pathlib import Path
from PIL import Image
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# 导入项目模块
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.improved_unet import ImprovedUNet
from data.dataset import CTPineWiltDataset


def visualize_training_curves(log_dir, output_dir):
    """可视化训练过程中的损失曲线和指标变化"""
    log_dir = Path(log_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找训练日志文件
    log_files = list(log_dir.glob("*.json")) + list(log_dir.glob("*.txt"))
    
    if not log_files:
        print(f"在 {log_dir} 中没有找到训练日志文件")
        return
    
    print(f"找到 {len(log_files)} 个日志文件")
    
    # 这里假设你有一个训练日志文件，格式为JSON
    # 如果没有，你可以从TensorBoard日志中提取数据
    for log_file in log_files:
        if log_file.suffix == ".json":
            with open(log_file, "r") as f:
                log_data = json.load(f)
                
            # 创建图表
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # 损失曲线
            if "train_loss" in log_data:
                axes[0, 0].plot(log_data["train_loss"], label="训练损失")
                axes[0, 0].plot(log_data["val_loss"], label="验证损失")
                axes[0, 0].set_xlabel("Epoch")
                axes[0, 0].set_ylabel("Loss")
                axes[0, 0].set_title("训练与验证损失")
                axes[0, 0].legend()
                axes[0, 0].grid(True)
            
            # Dice系数曲线
            if "dice" in log_data:
                axes[0, 1].plot(log_data["dice"], label="Dice系数")
                axes[0, 1].set_xlabel("Epoch")
                axes[0, 1].set_ylabel("Dice")
                axes[0, 1].set_title("Dice系数变化")
                axes[0, 1].legend()
                axes[0, 1].grid(True)
            
            # IoU曲线
            if "iou" in log_data:
                axes[1, 0].plot(log_data["iou"], label="IoU")
                axes[1, 0].set_xlabel("Epoch")
                axes[1, 0].set_ylabel("IoU")
                axes[1, 0].set_title("IoU变化")
                axes[1, 0].legend()
                axes[1, 0].grid(True)
            
            # 学习率曲线
            if "lr" in log_data:
                axes[1, 1].plot(log_data["lr"], label="学习率")
                axes[1, 1].set_xlabel("Epoch")
                axes[1, 1].set_ylabel("Learning Rate")
                axes[1, 1].set_title("学习率变化")
                axes[1, 1].set_yscale("log")
                axes[1, 1].legend()
                axes[1, 1].grid(True)
            
            plt.tight_layout()
            output_path = output_dir / f"{log_file.stem}_training_curves.png"
            plt.savefig(output_path, dpi=300)
            plt.close()
            print(f"训练曲线已保存: {output_path}")


def visualize_predictions(model_path, image_dir, output_dir, num_samples=5):
    """可视化模型预测结果对比"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载模型
    model = ImprovedUNet(n_channels=1, n_classes=1).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # 创建输出目录
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取测试图像
    image_dir = Path(image_dir)
    image_files = list(image_dir.glob("*.png"))[:num_samples]
    
    print(f"可视化 {len(image_files)} 个预测结果")
    
    with torch.no_grad():
        for i, img_path in enumerate(image_files):
            # 读取图像
            img = Image.open(img_path).convert("L")
            img_array = np.array(img)
            
            # 预处理
            img_tensor = torch.from_numpy(img_array).unsqueeze(0).unsqueeze(0).float().to(device) / 255.0
            
            # 推理
            output = model(img_tensor)
            pred_mask = (torch.sigmoid(output) > 0.5).float().cpu().numpy()[0, 0]
            
            # 读取真实掩码（如果存在）
            mask_path = img_path.parent.parent / "masks" / "test" / (img_path.stem + "_mask.png")
            has_mask = mask_path.exists()
            
            if has_mask:
                gt_mask = np.array(Image.open(mask_path).convert("L")) > 0
            
            # 创建可视化图表
            fig, axes = plt.subplots(1, 3 if has_mask else 2, figsize=(15, 5))
            
            # 原始图像
            axes[0].imshow(img_array, cmap="gray")
            axes[0].set_title("原始CT影像")
            axes[0].axis("off")
            
            # 预测掩码
            axes[1].imshow(pred_mask, cmap="jet", alpha=0.7)
            axes[1].imshow(img_array, cmap="gray", alpha=0.3)
            axes[1].set_title("预测分割结果")
            axes[1].axis("off")
            
            # 真实掩码（如果存在）
            if has_mask:
                axes[2].imshow(gt_mask, cmap="gray")
                axes[2].set_title("真实掩码")
                axes[2].axis("off")
            
            plt.tight_layout()
            output_path = output_dir / f"{img_path.stem}_prediction.png"
            plt.savefig(output_path, dpi=300)
            plt.close()
            print(f"[{i+1}/{len(image_files)}] 已保存: {output_path}")


def visualize_attention(model_path, image_path, output_dir):
    """可视化CBAM注意力热力图"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载模型
    model = ImprovedUNet(n_channels=1, n_classes=1).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # 创建输出目录
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取图像
    image_path = Path(image_path)
    img = Image.open(image_path).convert("L")
    img_array = np.array(img)
    
    # 预处理
    img_tensor = torch.from_numpy(img_array).unsqueeze(0).unsqueeze(0).float().to(device) / 255.0
    
    # 获取注意力权重
    with torch.no_grad():
        # 这里假设你的模型有方法可以获取注意力权重
        # 如果没有，你需要修改模型代码来返回注意力权重
        output, attention_weights = model(img_tensor, return_attention=True)
        
        # 可视化每个解码器块的注意力权重
        for block_name, attn_weight in attention_weights.items():
            attn_weight = attn_weight.cpu().numpy()[0, 0]  # 取第一个样本，第一个通道
            
            # 归一化到0-1
            attn_weight = (attn_weight - attn_weight.min()) / (attn_weight.max() - attn_weight.min() + 1e-8)
            
            # 上采样到原始图像大小
            attn_weight = cv2.resize(attn_weight, (img_array.shape[1], img_array.shape[0]))
            
            # 创建热力图
            plt.figure(figsize=(10, 5))
            
            plt.subplot(1, 2, 1)
            plt.imshow(img_array, cmap="gray")
            plt.title("原始CT影像")
            plt.axis("off")
            
            plt.subplot(1, 2, 2)
            plt.imshow(img_array, cmap="gray")
            plt.imshow(attn_weight, cmap="jet", alpha=0.5)
            plt.title(f"{block_name} 注意力热力图")
            plt.axis("off")
            
            plt.tight_layout()
            output_path = output_dir / f"{image_path.stem}_{block_name}_attention.png"
            plt.savefig(output_path, dpi=300)
            plt.close()
            print(f"注意力热力图已保存: {output_path}")


def visualize_confusion_matrix(confusion_matrix, class_names, output_dir):
    """可视化混淆矩阵"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(confusion_matrix, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names)
    plt.title("混淆矩阵")
    plt.ylabel("真实标签")
    plt.xlabel("预测标签")
    plt.tight_layout()
    
    output_path = output_dir / "confusion_matrix.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"混淆矩阵已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="可视化脚本")
    parser.add_argument("--mode", type=str, required=True, 
                        choices=["training", "prediction", "attention", "confusion"],
                        help="可视化模式")
    parser.add_argument("--log-dir", type=str, default="../results/",
                        help="训练日志目录")
    parser.add_argument("--model-path", type=str, default="../weights/improved_unet_best.pth",
                        help="模型权重路径")
    parser.add_argument("--image-path", type=str, default="../dataset/images/test/",
                        help="图像路径或目录")
    parser.add_argument("--output-dir", type=str, default="../results/visualizations/",
                        help="输出目录")
    parser.add_argument("--num-samples", type=int, default=5,
                        help="可视化样本数量")
    args = parser.parse_args()
    
    if args.mode == "training":
        visualize_training_curves(args.log_dir, args.output_dir)
    elif args.mode == "prediction":
        visualize_predictions(args.model_path, args.image_path, args.output_dir, args.num_samples)
    elif args.mode == "attention":
        visualize_attention(args.model_path, args.image_path, args.output_dir)
    elif args.mode == "confusion":
        # 这里需要你提供混淆矩阵数据
        # 例如：confusion_matrix = np.array([[TN, FP], [FN, TP]])
        # class_names = ["阴性", "阳性"]
        # visualize_confusion_matrix(confusion_matrix, class_names, args.output_dir)
        print("请先提供混淆矩阵数据")
    
    print("可视化完成!")


if __name__ == "__main__":
    main()