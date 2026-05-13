"""
CT图像松材线虫病检测系统 - 数据处理模块
包含数据加载、预处理、数据增强、去噪等功能
"""
import os
import json
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATASET_CONFIG, AUGMENTATION_CONFIG, DENOISING_CONFIG


# ======================== 图像去噪处理 ========================

class CTDenoiser:
    """CT图像去噪处理"""

    @staticmethod
    def bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
        """双边滤波 - 保边去噪"""
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

    @staticmethod
    def gaussian_filter(image, kernel=(5, 5)):
        """高斯滤波"""
        return cv2.GaussianBlur(image, kernel, 0)

    @staticmethod
    def median_filter(image, kernel=5):
        """中值滤波"""
        return cv2.medianBlur(image, kernel)

    @staticmethod
    def nlmeans_filter(image, h=10, templateWindowSize=7, searchWindowSize=21):
        """非局部均值去噪"""
        if len(image.shape) == 3:
            return cv2.fastNlMeansDenoisingColored(image, None, h, h,
                                                    templateWindowSize, searchWindowSize)
        return cv2.fastNlMeansDenoising(image, None, h,
                                         templateWindowSize, searchWindowSize)

    @staticmethod
    def denoise(image, method='bilateral', **kwargs):
        """统一去噪接口"""
        denoiser = CTDenoiser()
        if method == 'bilateral':
            return denoiser.bilateral_filter(image, **kwargs)
        elif method == 'gaussian':
            return denoiser.gaussian_filter(image, **kwargs)
        elif method == 'median':
            return denoiser.median_filter(image, **kwargs)
        elif method == 'nlmeans':
            return denoiser.nlmeans_filter(image, **kwargs)
        else:
            return image


# ======================== 标签格式转换 ========================

def labelme_to_mask(json_path, image_size=512, num_classes=2):
    """
    将LabelMe标注格式(JSON)转换为分割掩码

    LabelMe JSON格式包含shapes列表，每个shape有:
    - label: 标签名称
    - points: 多边形顶点坐标
    - shape_type: 形状类型(rectangle/polygon等)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    mask = np.zeros((image_size, image_size), dtype=np.uint8)

    # 标签映射
    label_map = {
        'background': 0,
        'Vector insect': 1,     # 松材线虫
        'pine_wilt': 1,         # 松材线虫病
        'hsdoiaihod': 1,        # 标注中的其他病害标签也映射为1
    }

    for shape in data.get('shapes', []):
        label = shape['label']
        points = shape['points']
        shape_type = shape.get('shape_type', 'rectangle')

        cls_id = label_map.get(label, 1)  # 未知标签默认为病变类

        if shape_type == 'rectangle':
            # 矩形标注
            pt1 = (int(points[0][0]), int(points[0][1]))
            pt2 = (int(points[1][0]), int(points[1][1]))
            cv2.rectangle(mask, pt1, pt2, cls_id, -1)
        elif shape_type == 'polygon':
            # 多边形标注
            pts = np.array(points, dtype=np.int32)
            cv2.fillPoly(mask, [pts], cls_id)
        elif shape_type == 'circle':
            # 圆形标注
            center = (int(points[0][0]), int(points[0][1]))
            radius = int(np.sqrt((points[1][0] - points[0][0])**2 +
                                  (points[1][1] - points[0][1])**2))
            cv2.circle(mask, center, radius, cls_id, -1)

    return mask


# ======================== 数据集类 ========================

class PineWiltDataset(Dataset):
    """松材线虫病CT图像数据集"""

    def __init__(self, image_dir, mask_dir=None, transform=None, is_train=True):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.transform = transform
        self.is_train = is_train

        # 获取所有图像文件
        self.images = sorted([f for f in os.listdir(image_dir)
                              if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))])

        if mask_dir:
            self.masks = sorted([f for f in os.listdir(mask_dir)
                                 if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))])
        else:
            self.masks = None

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        # 读取图像
        img_name = self.images[idx]
        img_path = os.path.join(self.image_dir, img_name)
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 读取掩码
        if self.masks and self.mask_dir:
            mask_name = self.masks[idx] if idx < len(self.masks) else img_name
            mask_path = os.path.join(self.mask_dir, mask_name)
            if os.path.exists(mask_path):
                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            else:
                mask = np.zeros(image.shape[:2], dtype=np.uint8)
        else:
            mask = np.zeros(image.shape[:2], dtype=np.uint8)

        # 数据增强
        if self.transform:
            augmented = self.transform(image=image, mask=mask)
            image = augmented['image']
            mask = augmented['mask']

        # 转换为Tensor
        if isinstance(image, np.ndarray):
            image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
        if isinstance(mask, np.ndarray):
            mask = torch.from_numpy(mask).long()

        return image, mask, img_name


# ======================== 数据增强 ========================

def get_train_transforms(image_size=512):
    """训练集数据增强"""
    return A.Compose([
        A.Resize(image_size, image_size),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.RandomRotate90(p=0.5),
        A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=30, p=0.5),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.3),
        A.GaussianBlur(blur_limit=3, p=0.2),
        A.GaussNoise(var_limit=(10, 50), p=0.2),
        A.ElasticTransform(alpha=1, sigma=50, p=0.2),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def get_val_transforms(image_size=512):
    """验证集/测试集变换"""
    return A.Compose([
        A.Resize(image_size, image_size),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


# ======================== 数据集构建 ========================

def build_dataloaders(data_dir, batch_size=4, num_workers=4, image_size=512):
    """构建训练、验证和测试数据加载器"""
    train_img_dir = os.path.join(data_dir, 'images', 'train')
    train_mask_dir = os.path.join(data_dir, 'masks', 'train')
    val_img_dir = os.path.join(data_dir, 'images', 'val')
    val_mask_dir = os.path.join(data_dir, 'masks', 'val')
    test_img_dir = os.path.join(data_dir, 'images', 'test')
    test_mask_dir = os.path.join(data_dir, 'masks', 'test')

    train_dataset = PineWiltDataset(
        train_img_dir, train_mask_dir,
        transform=get_train_transforms(image_size),
        is_train=True
    )

    val_dataset = PineWiltDataset(
        val_img_dir, val_mask_dir,
        transform=get_val_transforms(image_size),
        is_train=False
    )

    test_dataset = PineWiltDataset(
        test_img_dir, test_mask_dir,
        transform=get_val_transforms(image_size),
        is_train=False
    )

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size,
        shuffle=True, num_workers=num_workers,
        pin_memory=True, drop_last=True
    )

    val_loader = DataLoader(
        val_dataset, batch_size=batch_size,
        shuffle=False, num_workers=num_workers,
        pin_memory=True
    )

    test_loader = DataLoader(
        test_dataset, batch_size=1,
        shuffle=False, num_workers=num_workers,
        pin_memory=True
    )

    return train_loader, val_loader, test_loader


# ======================== 数据集预处理脚本 ========================

def prepare_dataset(source_dirs, output_dir, train_ratio=0.7, val_ratio=0.15):
    """
    将原始标注数据转换为训练格式

    source_dirs: 包含scan子目录的源数据目录列表
    output_dir: 输出目录
    """
    import random
    import shutil

    # 创建输出目录
    for split in ['train', 'val', 'test']:
        os.makedirs(os.path.join(output_dir, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'masks', split), exist_ok=True)

    # 收集所有图像和标注对
    pairs = []
    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            continue
        for scan_dir in os.listdir(source_dir):
            scan_path = os.path.join(source_dir, scan_dir)
            if not os.path.isdir(scan_path):
                continue
            for fname in os.listdir(scan_path):
                if fname.endswith('.json'):
                    json_path = os.path.join(scan_path, fname)
                    img_name = fname.replace('.json', '.png')
                    img_path = os.path.join(scan_path, img_name)
                    if os.path.exists(img_path):
                        pairs.append((img_path, json_path, img_name))

    print(f"共找到 {len(pairs)} 个图像-标注对")

    # 随机划分数据集
    random.seed(42)
    random.shuffle(pairs)

    n_total = len(pairs)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    train_pairs = pairs[:n_train]
    val_pairs = pairs[n_train:n_train + n_val]
    test_pairs = pairs[n_train + n_val:]

    print(f"训练集: {len(train_pairs)}, 验证集: {len(val_pairs)}, 测试集: {len(test_pairs)}")

    # 处理并保存
    denoiser = CTDenoiser()
    image_size = DATASET_CONFIG['image_size']

    for split, split_pairs in [('train', train_pairs), ('val', val_pairs), ('test', test_pairs)]:
        for img_path, json_path, img_name in split_pairs:
            # 读取图像
            image = cv2.imread(img_path)
            if image is None:
                continue

            # 去噪处理
            image = denoiser.denoise(image, method=DENOISING_CONFIG['method'])

            # 调整大小
            image = cv2.resize(image, (image_size, image_size))

            # 生成掩码
            mask = labelme_to_mask(json_path, image_size)
            mask = cv2.resize(mask, (image_size, image_size), interpolation=cv2.INTER_NEAREST)

            # 保存
            out_img_path = os.path.join(output_dir, 'images', split, img_name)
            out_mask_path = os.path.join(output_dir, 'masks', split, img_name)
            cv2.imwrite(out_img_path, image)
            cv2.imwrite(out_mask_path, mask)

    print("数据集准备完成！")
    return len(train_pairs), len(val_pairs), len(test_pairs)


if __name__ == '__main__':
    # 示例：准备数据集
    source_dirs = [
        r'D:\松材线虫\标注\first',
        r'D:\松材线虫\标注\third',
    ]
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dataset')
    prepare_dataset(source_dirs, output_dir)
