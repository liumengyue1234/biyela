#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型评估脚本
功能：1) 计算模型各项指标  2) 生成评估报告  3) 生成对比表格
用法：
  python evaluate.py --model-path ../weights/improved_unet_best.pth --model-type unet
  python evaluate.py --compare --model-dir ../weights/
"""

import argparse
import os
import json
import numpy as np
import torch
from pathlib import Path
from PIL import Image
import cv2
import sys
from collections import OrderedDict

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))

from models.improved_unet import ImprovedUNet
from models.mask_rcnn import PineWiltMaskRCNN
from utils.metrics import MetricsCalculator
from data.dataset import CTPineWiltDataset
from torch.utils.data import DataLoader


def evaluate_unet(model_path, data_dir, device="cuda"):
    """评估U-Net模型"""
    device = torch.device(device if torch.cuda.is_available() else "cpu")
    
    # 加载模型
    model = ImprovedUNet(n_channels=1, n_classes=1).to(device)
    
    # 处理可能的多GPU训练保存的权重
    state_dict = torch.load(model_path, map_location=device)
    if "module." in list(state_dict.keys())[0]:
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:]  # 去掉 `module.`
            new_state_dict[name] = v
        state_dict = new_state_dict
    
    model.load_state_dict(state_dict)
    model.eval()

    # 数据加载
    test_dataset = CTPineWiltDataset(
        images_dir=os.path.join(data_dir, "images/test"),
        masks_dir=os.path.join(data_dir, "masks/test"),
        transform=False
    )
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)

    calculator = MetricsCalculator()
    all_metrics = []

    print(f"开始评估 U-Net 模型: {model_path}")
    print("-" * 80)

    with torch.no_grad():
        for i, (images, masks) in enumerate(test_loader):
            images = images.to(device)
            masks = masks.to(device)

            outputs = model(images)
            preds = (torch.sigmoid(outputs) > 0.5).float()

            metrics = calculator.calculate_all_metrics(
                preds.cpu().numpy(),
                masks.cpu().numpy()
            )
            all_metrics.append(metrics)

            print(f"[{i+1}/{len(test_loader)}] "
                  f"Dice={metrics['dice']:.4f}  "
                  f"IoU={metrics['iou']:.4f}  "
                  f"Precision={metrics['precision']:.4f}  "
                  f"Recall={metrics['recall']:.4f}")

    # 计算平均指标
    avg_metrics = {}
    for key in all_metrics[0].keys():
        avg_metrics[key] = float(np.mean([m[key] for m in all_metrics]))

    print("-" * 80)
    print("平均指标：")
    for key, value in avg_metrics.items():
        print(f"  {key}: {value:.4f}")

    return avg_metrics


def evaluate_mask_rcnn(model_path, data_dir, device="cuda"):
    """评估Mask R-CNN模型"""
    device = torch.device(device if torch.cuda.is_available() else "cpu")
    
    model = PineWiltMaskRCNN(pretrained=False, num_classes=2)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval().to(device)

    calculator = MetricsCalculator()
    all_metrics = []

    print(f"开始评估 Mask R-CNN 模型: {model_path}")
    print("-" * 80)

    test_images_dir = Path(data_dir) / "images" / "test"
    image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))

    with torch.no_grad():
        for i, img_path in enumerate(image_files):
            mask_path = Path(data_dir) / "masks" / "test" / (img_path.stem + "_mask.png")
            if not mask_path.exists():
                continue

            # 读取并预处理图像
            img = Image.open(img_path).convert("L")
            img_array = np.array(img)
            img_tensor = torch.from_numpy(img_array).unsqueeze(0).unsqueeze(0).float().to(device) / 255.0
            
            # 推理
            outputs = model(img_tensor)
            
            if "masks" in outputs:
                pred_mask = (outputs["masks"] > 0.5).float()
                gt_mask = torch.from_numpy(np.array(Image.open(mask_path)) > 0).unsqueeze(0).unsqueeze(0).float()

                metrics = calculator.calculate_all_metrics(
                    pred_mask.cpu().numpy(),
                    gt_mask.cpu().numpy()
                )
                all_metrics.append(metrics)

            print(f"[{i+1}/{len(image_files)}] "
                  f"Dice={metrics.get('dice', 0):.4f}")

    # 计算平均指标
    avg_metrics = {}
    if all_metrics:
        for key in all_metrics[0].keys():
            avg_metrics[key] = float(np.mean([m[key] for m in all_metrics]))

        print("-" * 80)
        print("平均指标：")
        for key, value in avg_metrics.items():
            print(f"  {key}: {value:.4f}")
    else:
        # 如果没有有效的评估数据，返回默认值
        avg_metrics = {
            'dice': 0.0,
            'iou': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1': 0.0,
            'accuracy': 0.0,
            'hausdorff': 0.0
        }
        print("警告: 没有有效的评估数据")

    return avg_metrics


def generate_report(metrics_dict, model_name, output_dir):
    """生成评估报告（Markdown格式）"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = output_dir / f"evaluation_report_{model_name}.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# {model_name} 评估报告\n\n")
        f.write(f"生成时间: {Path(__file__).stem}\n\n")
        f.write("---\n\n")
        f.write("## 评估指标\n\n")
        f.write("| 指标 | 值 |\n")
        f.write("|------|------|\n")
        for key, value in metrics_dict.items():
            f.write(f"| {key} | {value:.4f} |\n")
        
        f.write("\n---\n\n")
        f.write("## 指标说明\n\n")
        f.write("- **Dice系数**: 衡量分割重叠程度，取值范围0-1，越大越好\n")
        f.write("- **IoU**: 交并比，衡量预测与真实区域的重叠程度\n")
        f.write("- **精确率(Precision)**: 预测为正的样本中真正为正的比例\n")
        f.write("- **召回率(Recall)**: 真正为正的样本中被预测为正的比例\n")
        f.write("- **F1分数**: Precision和Recall的调和平均数\n")
        f.write("- **准确率(Accuracy)**: 所有样本中预测正确的比例\n")
        f.write("- **Hausdorff距离**: 测量预测边界与真实边界的最大距离，越小越好\n")
    
    print(f"评估报告已保存: {report_path}")
    return report_path


def generate_comparison_table(metrics_list, output_path):
    """生成模型对比表格"""
    output_path = Path(output_path)
    metrics_keys = ["dice", "iou", "precision", "recall", "f1", "accuracy", "hausdorff"]
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 模型对比报告\n\n")
        f.write("| 模型 | ")
        f.write(" | ".join([k.upper() for k in metrics_keys]))
        f.write(" |\n")
        
        f.write("|------|")
        f.write("|".join(["---"] * len(metrics_keys)))
        f.write("|\n")
        
        for item in metrics_list:
            f.write(f"| {item['model_name']} | ")
            f.write(" | ".join([f"{item['metrics'].get(k, 0):.4f}" for k in metrics_keys]))
            f.write(" |\n")
    
    print(f"对比表格已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="模型评估脚本")
    parser.add_argument("--model-path", type=str, help="模型权重路径")
    parser.add_argument("--model-type", type=str, choices=["unet", "mask_rcnn"],
                        help="模型类型")
    parser.add_argument("--data-dir", type=str, default="../../dataset",
                        help="数据集根目录")
    parser.add_argument("--output-dir", type=str, default="../results",
                        help="评估结果输出目录")
    parser.add_argument("--compare", action="store_true",
                        help="对比多个模型")
    parser.add_argument("--model-dir", type=str,
                        help="模型权重目录（用于对比）")
    args = parser.parse_args()
    
    if args.compare and args.model_dir:
        # 对比多个模型
        model_dir = Path(args.model_dir)
        metrics_list = []
        
        for weight_file in model_dir.glob("*.pth"):
            print(f"\n评估模型: {weight_file.name}")
            if "unet" in weight_file.name:
                metrics = evaluate_unet(str(weight_file), args.data_dir)
                metrics_list.append({
                    "model_name": weight_file.stem,
                    "metrics": metrics
                })
        
        if metrics_list:
            output_path = Path(args.output_dir) / "model_comparison.md"
            generate_comparison_table(metrics_list, output_path)
    
    elif args.model_path and args.model_type:
        if args.model_type == "unet":
            metrics = evaluate_unet(args.model_path, args.data_dir)
        elif args.model_type == "mask_rcnn":
            metrics = evaluate_mask_rcnn(args.model_path, args.data_dir)
        
        generate_report(metrics, Path(args.model_path).stem, args.output_dir)
    
    else:
        print("请指定 --model-path 和 --model-type，或使用 --compare 进行模型对比")
        print("使用 --help 查看帮助")


if __name__ == "__main__":
    main()