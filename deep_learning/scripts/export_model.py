#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型导出脚本
功能：1) 将PyTorch模型导出为ONNX格式  2) 导出为TorchScript格式  3) 验证导出模型的正确性
用法：
  python export_model.py --model-path ../weights/improved_unet_best.pth --model-type unet --output ../weights/
  python export_model.py --model-path ../weights/mask_rcnn_best.pth --model-type mask_rcnn --output ../weights/ --export-onnx
"""

import argparse
import os
import torch
import numpy as np
from pathlib import Path
import onnx
import onnxruntime as ort

# 导入项目模块
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.improved_unet import ImprovedUNet
from models.mask_rcnn import PineWiltMaskRCNN
from utils.metrics import MetricsCalculator
from data.dataset import CTPineWiltDataset


def export_unet_to_onnx(model_path, output_dir, input_size=(1, 1, 256, 256)):
    """将U-Net模型导出为ONNX格式"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载模型
    model = ImprovedUNet(n_channels=1, n_classes=1).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # 创建示例输入
    dummy_input = torch.randn(input_size).to(device)
    
    # 导出ONNX
    output_path = Path(output_dir) / "improved_unet.onnx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    torch.onnx.export(
        model,
        dummy_input,
        str(output_path),
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    print(f"U-Net模型已导出为ONNX: {output_path}")
    
    # 验证ONNX模型
    onnx_model = onnx.load(str(output_path))
    onnx.checker.check_model(onnx_model)
    print("ONNX模型验证通过!")
    
    # 使用ONNX Runtime测试推理
    ort_session = ort.InferenceSession(str(output_path))
    test_input = np.random.randn(*input_size).astype(np.float32)
    ort_inputs = {ort_session.get_inputs()[0].name: test_input}
    ort_outputs = ort_session.run(None, ort_inputs)
    print(f"ONNX Runtime推理测试通过! 输出形状: {ort_outputs[0].shape}")
    
    return str(output_path)


def export_unet_to_torchscript(model_path, output_dir):
    """将U-Net模型导出为TorchScript格式"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载模型
    model = ImprovedUNet(n_channels=1, n_classes=1).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # 创建示例输入
    dummy_input = torch.randn(1, 1, 256, 256).to(device)
    
    # 导出TorchScript
    output_path = Path(output_dir) / "improved_unet.pt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 使用tracing方式导出
    traced_script_module = torch.jit.trace(model, dummy_input)
    traced_script_module.save(str(output_path))
    
    print(f"U-Net模型已导出为TorchScript: {output_path}")
    
    # 验证TorchScript模型
    loaded_model = torch.jit.load(str(output_path))
    test_input = torch.randn(1, 1, 256, 256)
    output = loaded_model(test_input)
    print(f"TorchScript模型验证通过! 输出形状: {output.shape}")
    
    return str(output_path)


def export_mask_rcnn_to_onnx(model_path, output_dir, input_size=(1, 1, 256, 256)):
    """将Mask R-CNN模型导出为ONNX格式"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载模型
    model = PineWiltMaskRCNN(pretrained=False, num_classes=2)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval().to(device)
    
    # 创建示例输入
    dummy_input = torch.randn(input_size).to(device)
    
    # 导出ONNX
    output_path = Path(output_dir) / "mask_rcnn.onnx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    torch.onnx.export(
        model,
        dummy_input,
        str(output_path),
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['masks', 'boxes', 'labels', 'scores'],
        dynamic_axes={'input': {0: 'batch_size'}}
    )
    
    print(f"Mask R-CNN模型已导出为ONNX: {output_path}")
    
    # 验证ONNX模型
    try:
        onnx_model = onnx.load(str(output_path))
        onnx.checker.check_model(onnx_model)
        print("ONNX模型验证通过!")
    except Exception as e:
        print(f"ONNX模型验证警告: {e}")
    
    return str(output_path)


def export_yolo_to_onnx(model_path, output_dir):
    """将YOLO模型导出为ONNX格式"""
    try:
        from ultralytics import YOLO
        
        # 加载YOLO模型
        model = YOLO(model_path)
        
        # 导出ONNX
        output_path = Path(output_dir) / "yolov8.onnx"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用YOLO内置的导出功能
        model.export(format="onnx", opset=11, simplify=True)
        
        print(f"YOLO模型已导出为ONNX: {output_path}")
        return str(output_path)
    except ImportError:
        print("请先安装 ultralytics: pip install ultralytics")
        return None
    except Exception as e:
        print(f"YOLO模型导出失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="模型导出脚本")
    parser.add_argument("--model-path", type=str, required=True,
                        help="模型权重路径")
    parser.add_argument("--model-type", type=str, required=True, choices=["unet", "mask_rcnn", "yolo"],
                        help="模型类型")
    parser.add_argument("--output-dir", type=str, default="../weights/",
                        help="输出目录")
    parser.add_argument("--export-onnx", action="store_true",
                        help="导出为ONNX格式")
    parser.add_argument("--export-torchscript", action="store_true",
                        help="导出为TorchScript格式")
    parser.add_argument("--input-size", type=int, nargs=4, default=[1, 1, 256, 256],
                        help="输入尺寸 (batch, channel, height, width)")
    args = parser.parse_args()
    
    # 如果没有指定导出格式，默认导出ONNX
    if not args.export_onnx and not args.export_torchscript:
        args.export_onnx = True
    
    print(f"开始导出 {args.model_type} 模型: {args.model_path}")
    print(f"输出目录: {args.output_dir}")
    
    exported_files = []
    
    if args.model_type == "unet":
        if args.export_onnx:
            onnx_path = export_unet_to_onnx(args.model_path, args.output_dir, tuple(args.input_size))
            if onnx_path:
                exported_files.append(onnx_path)
        
        if args.export_torchscript:
            ts_path = export_unet_to_torchscript(args.model_path, args.output_dir)
            if ts_path:
                exported_files.append(ts_path)
    
    elif args.model_type == "mask_rcnn":
        if args.export_onnx:
            onnx_path = export_mask_rcnn_to_onnx(args.model_path, args.output_dir, tuple(args.input_size))
            if onnx_path:
                exported_files.append(onnx_path)
    
    elif args.model_type == "yolo":
        if args.export_onnx:
            onnx_path = export_yolo_to_onnx(args.model_path, args.output_dir)
            if onnx_path:
                exported_files.append(onnx_path)
    
    print("\n导出完成!")
    for file in exported_files:
        print(f"  - {file}")
    
    if not exported_files:
        print("警告: 没有成功导出任何模型文件")


if __name__ == "__main__":
    main()