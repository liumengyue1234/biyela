"""
CT图像松材线虫病检测系统 - 深度学习模块配置文件
包含所有模型训练和评估的配置参数
"""
import os

# ==================== 项目路径配置 ====================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, '..', 'dataset')
CHECKPOINT_DIR = os.path.join(PROJECT_ROOT, 'checkpoints')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

# 数据集路径
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MASK_DIR = os.path.join(DATA_DIR, 'masks')
ANNOTATION_DIR = os.path.join(DATA_DIR, 'annotations')

# ==================== 数据集配置 ====================
DATASET_CONFIG = {
    'image_size': 512,           # 输入图像尺寸
    'mask_size': 512,            # 掩码尺寸
    'train_ratio': 0.7,          # 训练集比例
    'val_ratio': 0.15,           # 验证集比例
    'test_ratio': 0.15,          # 测试集比例
    'num_workers': 4,            # 数据加载线程数
    'num_classes': 2,            # 分类数（背景+病变区域）
    'class_names': ['background', 'pine_wilt'],  # 类别名称
}

# ==================== 数据增强配置 ====================
AUGMENTATION_CONFIG = {
    'horizontal_flip': True,     # 水平翻转
    'vertical_flip': True,       # 垂直翻转
    'rotation_range': 30,        # 旋转角度范围
    'brightness_range': 0.2,     # 亮度调整范围
    'contrast_range': 0.2,       # 对比度调整范围
    'gaussian_noise': True,      # 高斯噪声
    'gaussian_blur': True,       # 高斯模糊
    'random_crop': True,         # 随机裁剪
    'elastic_transform': True,   # 弹性变形
}

# ==================== 改进U-Net模型配置 ====================
IMPROVED_UNET_CONFIG = {
    'name': 'ImprovedUNet',
    'in_channels': 3,
    'out_channels': 2,
    'base_filters': 64,
    'use_cbam': True,            # 使用CBAM注意力机制
    'use_residual': True,        # 使用残差连接
    'use_multiscale': True,      # 使用多尺度特征融合
    'cbam_reduction': 16,        # CBAM通道缩减比例
    'dropout_rate': 0.3,         # Dropout比率
}

# ==================== 改进U-Net训练配置 ====================
IMPROVED_UNET_TRAIN_CONFIG = {
    'batch_size': 4,
    'epochs_phase1': 50,         # 第一阶段训练轮数
    'epochs_phase2': 30,         # 第二阶段训练轮数
    'lr_phase1': 1e-4,           # 第一阶段学习率
    'lr_phase2': 1e-5,           # 第二阶段学习率
    'weight_decay': 1e-4,
    'optimizer': 'AdamW',
    'scheduler': 'CosineAnnealingLR',
    'dice_weight': 0.5,          # Dice损失权重
    'ce_weight': 0.5,            # 交叉熵损失权重
    'freeze_encoder_layers': 3,  # 冻结编码端前3层
    'early_stopping_patience': 10,
    'save_top_k': 3,
}

# ==================== 标准U-Net模型配置（对比用） ====================
STANDARD_UNET_CONFIG = {
    'name': 'StandardUNet',
    'in_channels': 3,
    'out_channels': 2,
    'base_filters': 64,
}

STANDARD_UNET_TRAIN_CONFIG = {
    'batch_size': 4,
    'epochs': 80,
    'lr': 1e-4,
    'weight_decay': 1e-4,
    'optimizer': 'AdamW',
    'scheduler': 'CosineAnnealingLR',
    'dice_weight': 0.5,
    'ce_weight': 0.5,
}

# ==================== Mask R-CNN模型配置 ====================
MASK_RCNN_CONFIG = {
    'name': 'MaskRCNN',
    'backbone': 'resnet50',
    'num_classes': 2,            # 背景+病变
    'pretrained': True,
    'min_size': 512,
    'max_size': 512,
    'rpn_anchor_sizes': ((32,), (64,), (128,), (256,), (512,)),
    'rpn_anchor_aspect_ratios': ((0.5, 1.0, 2.0),) * 5,
    'roi_detections_per_img': 100,
    'roi_score_thresh': 0.05,
    'roi_nms_thresh': 0.5,
    'roi_fg_iou_thresh': 0.5,
    'roi_bg_iou_thresh': 0.5,
}

MASK_RCNN_TRAIN_CONFIG = {
    'batch_size': 2,
    'epochs': 50,
    'lr': 1e-4,
    'weight_decay': 1e-4,
    'optimizer': 'SGD',
    'momentum': 0.9,
    'scheduler': 'StepLR',
    'step_size': 15,
    'gamma': 0.1,
}

# ==================== YOLO系列模型配置 ====================
YOLO_CONFIGS = {
    'yolov8': {
        'name': 'YOLOv8',
        'model_size': 's',       # n, s, m, l, x
        'task': 'segment',       # 分割任务
        'imgsz': 512,
        'batch_size': 8,
        'epochs': 100,
        'lr0': 1e-3,
        'weight_decay': 5e-4,
        'optimizer': 'AdamW',
        'patience': 20,           # early stopping
        'augment': True,
        'mosaic': 1.0,
        'mixup': 0.1,
    },
    'yolov10': {
        'name': 'YOLOv10',
        'model_size': 's',
        'task': 'segment',
        'imgsz': 512,
        'batch_size': 8,
        'epochs': 100,
        'lr0': 1e-3,
        'weight_decay': 5e-4,
        'optimizer': 'AdamW',
        'patience': 20,
        'augment': True,
        'mosaic': 1.0,
        'mixup': 0.1,
    },
    'yolov11': {
        'name': 'YOLOv11',
        'model_size': 's',
        'task': 'segment',
        'imgsz': 512,
        'batch_size': 8,
        'epochs': 100,
        'lr0': 1e-3,
        'weight_decay': 5e-4,
        'optimizer': 'AdamW',
        'patience': 20,
        'augment': True,
        'mosaic': 1.0,
        'mixup': 0.1,
    },
}

# ==================== 评估指标配置 ====================
EVALUATION_CONFIG = {
    'metrics': ['dice', 'iou', 'precision', 'recall', 'f1', 'accuracy', 'hausdorff'],
    'threshold': 0.5,            # 二值化阈值
    'save_predictions': True,    # 保存预测结果
    'save_comparison': True,     # 保存对比图
}

# ==================== 去噪配置 ====================
DENOISING_CONFIG = {
    'method': 'bilateral',       # bilateral, gaussian, median, nlmeans
    'bilateral_d': 9,            # bilateral滤波邻域直径
    'bilateral_sigma_color': 75, # bilateral颜色空间标准差
    'bilateral_sigma_space': 75, # bilateral坐标空间标准差
    'gaussian_kernel': (5, 5),    # 高斯滤波核大小
    'median_kernel': 5,          # 中值滤波核大小
}
