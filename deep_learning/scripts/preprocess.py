#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CT影像数据预处理脚本
功能：1) DICOM转PNG/JPG  2) 图像去噪
      3) 标注格式转换（LabelMe JSON -> Mask） 4) 数据集统计
用法：
  python preprocess.py --input ./dataset/raw --output ./dataset --convert-dcm
  python preprocess.py --input ./dataset/raw --output ./dataset --denoise bilateral
"""

import argparse
import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import json


def convert_dcm_to_png(input_dir, output_dir, target_size=None):
    """将DICOM格式转换为PNG格式"""
    try:
        import pydicom
    except ImportError:
        print("请先安装 pydicom: pip install pydicom")
        return

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dcm_files = list(input_dir.rglob("*.dcm"))
    print(f"找到 {len(dcm_files)} 个DICOM文件")

    for i, dcm_path in enumerate(dcm_files):
        try:
            ds = pydicom.dcmread(str(dcm_path))
            pixel_array = ds.pixel_array.astype(np.float32)

            # 归一化到0-255
            pixel_array = (pixel_array - pixel_array.min()) / \
                         (pixel_array.max() - pixel_array.min() + 1e-8) * 255
            pixel_array = pixel_array.astype(np.uint8)

            if target_size:
                pixel_array = cv2.resize(pixel_array, target_size)

            output_path = output_dir / (dcm_path.stem + ".png")
            Image.fromarray(pixel_array).save(output_path)
            print(f"[{i+1}/{len(dcm_files)}] {dcm_path.name} -> {output_path.name}")
        except Exception as e:
            print(f"转换失败 {dcm_path.name}: {e}")


def denoise_image(image, method="bilateral", **kwargs):
    """图像去噪"""
    if method == "bilateral":
        d = kwargs.get("diameter", 9)
        sigma_color = kwargs.get("sigma_color", 75)
        sigma_space = kwargs.get("sigma_space", 75)
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
    elif method == "gaussian":
        ksize = kwargs.get("ksize", (5, 5))
        return cv2.GaussianBlur(image, ksize, 0)
    elif method == "median":
        ksize = kwargs.get("ksize", 5)
        return cv2.medianBlur(image, ksize)
    elif method == "nlmeans":
        try:
            import skimage.restoration
            return skimage.restoration.denoise_nl_means(
                image, multichannel=False)
        except ImportError:
            print("请先安装 scikit-image: pip install scikit-image")
            return image
    else:
        return image


def batch_denoise(input_dir, output_dir, method="bilateral"):
    """批量去噪"""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_files = list(input_dir.glob("*.png")) + \
                 list(input_dir.glob("*.jpg")) + \
                 list(input_dir.glob("*.jpeg"))

    print(f"找到 {len(image_files)} 张图片，使用 {method} 去噪...")

    for i, img_path in enumerate(image_files):
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        denoised = denoise_image(img, method)
        if denoised.dtype != np.uint8:
            denoised = (denoised * 255).astype(np.uint8)
        output_path = output_dir / img_path.name
        cv2.imwrite(str(output_path), denoised)
        print(f"[{i+1}/{len(image_files)}] {img_path.name}")


def labelme_to_mask(labelme_json_path, output_mask_dir):
    """将LabelMe标注转换为分割Mask"""
    json_path = Path(labelme_json_path)
    output_dir = Path(output_mask_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    img_h = data["imageHeight"]
    img_w = data["imageWidth"]
    mask = np.zeros((img_h, img_w), dtype=np.uint8)

    for shape in data["shapes"]:
        points = np.array(shape["points"], dtype=np.int32)
        if shape["shape_type"] == "polygon":
            cv2.fillPoly(mask, [points], 255)
        elif shape["shape_type"] == "rectangle":
            x1, y1 = points[0]
            x2, y2 = points[1]
            cv2.rectangle(mask, (int(x1), int(y1)), (int(x2), int(y2)), 255, -1)

    output_path = output_dir / (json_path.stem + "_mask.png")
    cv2.imwrite(str(output_path), mask)
    print(f"Mask已保存: {output_path}")
    return output_path


def print_dataset_stats(dataset_dir):
    """打印数据集统计信息"""
    dataset_dir = Path(dataset_dir)
    splits = ["train", "val", "test"]

    print("=" * 60)
    print("数据集统计信息")
    print("=" * 60)

    for split in splits:
        img_dir = dataset_dir / "images" / split
        mask_dir = dataset_dir / "masks" / split

        if img_dir.exists():
            imgs = list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpg"))
            print(f"\n[{split.upper()}]")
            print(f"  图像数量: {len(imgs)}")

            if mask_dir.exists():
                masks = list(mask_dir.glob("*.png"))
                print(f"  Mask数量: {len(masks)}")
                if len(imgs) != len(masks):
                    print(f"  ⚠ 图像与Mask数量不匹配！")

            # 采样一张图像查看尺寸
            if imgs:
                img = cv2.imread(str(imgs[0]), cv2.IMREAD_GRAYSCALE)
                print(f"  图像尺寸: {img.shape}")


def main():
    parser = argparse.ArgumentParser(description="CT影像数据预处理脚本")
    parser.add_argument("--input", type=str, help="输入目录")
    parser.add_argument("--output", type=str, help="输出目录")
    parser.add_argument("--convert-dcm", action="store_true", help="转换DICOM到PNG")
    parser.add_argument("--denoise", type=str, choices=["bilateral", "gaussian", "median", "nlmeans"],
                        help="去噪方法")
    parser.add_argument("--labelme-to-mask", action="store_true", help="转换LabelMe标注为Mask")
    parser.add_argument("--stats", action="store_true", help="显示数据集统计")
    parser.add_argument("--target-size", type=int, nargs=2, default=None, help="目标尺寸 H W")
    args = parser.parse_args()

    if args.convert_dcm and args.input and args.output:
        convert_dcm_to_png(args.input, args.output, tuple(args.target_size) if args.target_size else None)

    if args.denoise and args.input and args.output:
        batch_denoise(args.input, args.output, args.denoise)

    if args.labelme_to_mask and args.input and args.output:
        labelme_to_mask(args.input, args.output)

    if args.stats and args.input:
        print_dataset_stats(args.input)

    if not any([args.convert_dcm, args.denoise, args.labelme_to_mask, args.stats]):
        print("请指定操作参数，使用 --help 查看帮助")


if __name__ == "__main__":
    main()
