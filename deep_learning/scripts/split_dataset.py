#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据集划分脚本
功能：1) 将原始数据集划分为训练集、验证集和测试集  2) 支持按比例划分  3) 支持分层抽样
用法：
  python split_dataset.py --input-dir ../dataset/raw --output-dir ../dataset
  python split_dataset.py --input-dir ../dataset/raw --output-dir ../dataset --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15
"""

import argparse
import os
import shutil
import random
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split


def split_dataset(input_dir, output_dir, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, 
                  random_seed=42, copy_files=True):
    """
    将数据集划分为训练集、验证集和测试集
    
    Args:
        input_dir: 输入目录，包含images和masks子目录
        output_dir: 输出目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
        random_seed: 随机种子
        copy_files: 是否复制文件（True）或移动文件（False）
    """
    # 验证比例之和是否为1
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
        raise ValueError(f"比例之和必须为1.0，当前为{train_ratio + val_ratio + test_ratio}")
    
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    # 创建输出目录结构
    splits = ['train', 'val', 'test']
    for split in splits:
        (output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_dir / 'masks' / split).mkdir(parents=True, exist_ok=True)
    
    # 获取所有图像文件
    images_dir = input_dir / 'images'
    if not images_dir.exists():
        print(f"错误：输入目录中找不到images子目录: {images_dir}")
        return
    
    # 支持多种图像格式
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tif', '*.tiff']:
        image_files.extend(list(images_dir.glob(ext)))
    
    if not image_files:
        print(f"警告：在 {images_dir} 中没有找到图像文件")
        return
    
    print(f"找到 {len(image_files)} 个图像文件")
    
    # 设置随机种子
    random.seed(random_seed)
    np.random.seed(random_seed)
    
    # 首先划分训练集和临时集（验证集+测试集）
    train_files, temp_files = train_test_split(
        image_files, test_size=(val_ratio + test_ratio), random_state=random_seed
    )
    
    # 然后将临时集划分为验证集和测试集
    val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
    val_files, test_files = train_test_split(
        temp_files, test_size=(1 - val_ratio_adjusted), random_state=random_seed
    )
    
    print(f"数据集划分完成:")
    print(f"  训练集: {len(train_files)} 个样本 ({len(train_files)/len(image_files)*100:.1f}%)")
    print(f"  验证集: {len(val_files)} 个样本 ({len(val_files)/len(image_files)*100:.1f}%)")
    print(f"  测试集: {len(test_files)} 个样本 ({len(test_files)/len(image_files)*100:.1f}%)")
    
    # 复制或移动文件
    def process_files(file_list, split_name):
        """处理文件列表，复制到对应的输出目录"""
        count = 0
        for img_path in file_list:
            # 目标图像路径
            target_img_path = output_dir / 'images' / split_name / img_path.name
            
            # 对应的mask路径（假设mask文件名与图像文件名相同，扩展名为.png）
            mask_path = input_dir / 'masks' / (img_path.stem + '_mask.png')
            target_mask_path = output_dir / 'masks' / split_name / (img_path.stem + '_mask.png')
            
            # 复制或移动图像文件
            if copy_files:
                shutil.copy2(img_path, target_img_path)
            else:
                shutil.move(img_path, target_img_path)
            
            # 复制或移动mask文件（如果存在）
            if mask_path.exists():
                if copy_files:
                    shutil.copy2(mask_path, target_mask_path)
                else:
                    shutil.move(mask_path, target_mask_path)
                count += 1
            else:
                print(f"警告：找不到对应的mask文件: {mask_path}")
        
        return count
    
    # 处理各个划分
    print(f"\n开始{'复制' if copy_files else '移动'}文件...")
    train_count = process_files(train_files, 'train')
    val_count = process_files(val_files, 'val')
    test_count = process_files(test_files, 'test')
    
    print(f"处理完成:")
    print(f"  训练集: {train_count} 个mask文件已处理")
    print(f"  验证集: {val_count} 个mask文件已处理")
    print(f"  测试集: {test_count} 个mask文件已处理")
    
    # 创建数据集信息文件
    create_dataset_info(output_dir, train_files, val_files, test_files)
    
    print(f"\n数据集划分完成！输出目录: {output_dir}")


def create_dataset_info(output_dir, train_files, val_files, test_files):
    """创建数据集信息文件"""
    info_path = output_dir / 'dataset_info.txt'
    
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write("# 数据集划分信息\n\n")
        f.write(f"总样本数: {len(train_files) + len(val_files) + len(test_files)}\n")
        f.write(f"训练集: {len(train_files)} 个样本\n")
        f.write(f"验证集: {len(val_files)} 个样本\n")
        f.write(f"测试集: {len(test_files)} 个样本\n\n")
        
        f.write("# 训练集文件列表\n")
        for img_path in train_files:
            f.write(f"{img_path.name}\n")
        
        f.write("\n# 验证集文件列表\n")
        for img_path in val_files:
            f.write(f"{img_path.name}\n")
        
        f.write("\n# 测试集文件列表\n")
        for img_path in test_files:
            f.write(f"{img_path.name}\n")
    
    print(f"数据集信息已保存到: {info_path}")


def main():
    parser = argparse.ArgumentParser(description="数据集划分脚本")
    parser.add_argument("--input-dir", type=str, required=True,
                        help="输入目录，包含images和masks子目录")
    parser.add_argument("--output-dir", type=str, required=True,
                        help="输出目录")
    parser.add_argument("--train-ratio", type=float, default=0.7,
                        help="训练集比例 (默认: 0.7)")
    parser.add_argument("--val-ratio", type=float, default=0.15,
                        help="验证集比例 (默认: 0.15)")
    parser.add_argument("--test-ratio", type=float, default=0.15,
                        help="测试集比例 (默认: 0.15)")
    parser.add_argument("--seed", type=int, default=42,
                        help="随机种子 (默认: 42)")
    parser.add_argument("--move", action="store_true",
                        help="移动文件而不是复制 (默认: 复制)")
    
    args = parser.parse_args()
    
    # 验证比例
    if abs(args.train_ratio + args.val_ratio + args.test_ratio - 1.0) > 1e-6:
        print(f"错误：比例之和必须为1.0，当前为{args.train_ratio + args.val_ratio + args.test_ratio}")
        return
    
    print("=" * 60)
    print("数据集划分脚本")
    print("=" * 60)
    print(f"输入目录: {args.input_dir}")
    print(f"输出目录: {args.output_dir}")
    print(f"训练集比例: {args.train_ratio}")
    print(f"验证集比例: {args.val_ratio}")
    print(f"测试集比例: {args.test_ratio}")
    print(f"随机种子: {args.seed}")
    print(f"操作: {'移动文件' if args.move else '复制文件'}")
    print("=" * 60)
    
    split_dataset(
        args.input_dir, 
        args.output_dir, 
        args.train_ratio, 
        args.val_ratio, 
        args.test_ratio, 
        args.seed,
        not args.move  # copy_files = not move
    )


if __name__ == "__main__":
    main()