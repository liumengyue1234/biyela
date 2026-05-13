"""
CT图像松材线虫病检测系统 - Mask R-CNN模型
基于torchvision的Mask R-CNN实现，用于CT图像的实例分割检测
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models.detection import maskrcnn_resnet50_fpn_v2
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor


def build_mask_rcnn(num_classes=3, pretrained=True, backbone='resnet50'):
    """
    构建Mask R-CNN模型

    Args:
        num_classes: 类别数 (包含背景类)
            - 1: 背景
            - 2: 松材线虫病区域
            - 3: 其他病变 (可选)
        pretrained: 是否使用COCO预训练权重
        backbone: 骨干网络类型

    Returns:
        model: Mask R-CNN模型
    """
    # 使用v2版本，性能更好
    model = maskrcnn_resnet50_fpn_v2(pretrained=pretrained)

    # ========= 修改分类头 =========
    # 获取原分类器的输入维度
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # 替换为新的分类头 (num_classes包含背景)
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    # ========= 修改Mask预测头 =========
    # 获取原Mask预测器的输入维度
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256
    # 替换为新的Mask预测头
    model.roi_heads.mask_predictor = MaskRCNNPredictor(
        in_features_mask,
        hidden_layer,
        num_classes
    )

    return model


class PineWiltMaskRCNN:
    """
    松材线虫病Mask R-CNN检测器
    封装模型构建、推理和后处理
    """

    def __init__(self, num_classes=2, device='cuda', score_threshold=0.5,
                 nms_threshold=0.5, mask_threshold=0.5):
        """
        Args:
            num_classes: 类别数 (包含背景)
            device: 计算设备
            score_threshold: 检测置信度阈值
            nms_threshold: 非极大值抑制阈值
            mask_threshold: Mask二值化阈值
        """
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.num_classes = num_classes
        self.score_threshold = score_threshold
        self.nms_threshold = nms_threshold
        self.mask_threshold = mask_threshold

        # 构建模型
        self.model = build_mask_rcnn(num_classes=num_classes)
        self.model.to(self.device)

    def load_weights(self, weight_path):
        """加载模型权重"""
        checkpoint = torch.load(weight_path, map_location=self.device)
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)
        print(f"权重已加载: {weight_path}")

    def preprocess(self, image):
        """
        图像预处理

        Args:
            image: numpy array (H, W, C) 或 (C, H, W)

        Returns:
            tensor: 预处理后的张量
        """
        import numpy as np
        from torchvision import transforms

        if isinstance(image, np.ndarray):
            # 确保是 (H, W, C) 格式
            if image.ndim == 2:
                image = np.stack([image] * 3, axis=-1)
            elif image.shape[0] == 3 and image.ndim == 3:
                image = np.transpose(image, (1, 2, 0))

            # 归一化到 [0, 1]
            if image.dtype == np.uint8:
                image = image.astype(np.float32) / 255.0

            # 转为张量 (C, H, W)
            image = torch.from_numpy(image).permute(2, 0, 1).float()

        return image

    def predict(self, images, return_masks=True):
        """
        执行推理

        Args:
            images: 单张图像或图像列表 (tensor格式)
            return_masks: 是否返回分割掩码

        Returns:
            results: 检测结果列表
        """
        self.model.eval()

        if not isinstance(images, (list, tuple)):
            images = [images]

        # 将图像移到设备
        images = [img.to(self.device) for img in images]

        with torch.no_grad():
            outputs = self.model(images)

        # 后处理结果
        results = []
        for output in outputs:
            result = self._postprocess(output)
            results.append(result)

        return results[0] if len(results) == 1 else results

    def _postprocess(self, output):
        """
        后处理模型输出

        Args:
            output: 模型原始输出

        Returns:
            processed: 处理后的结果字典
        """
        # 过滤低置信度检测结果
        scores = output['scores'].cpu()
        keep = scores > self.score_threshold

        boxes = output['boxes'].cpu()[keep]
        labels = output['labels'].cpu()[keep]
        scores = scores[keep]

        result = {
            'boxes': boxes,
            'labels': labels,
            'scores': scores,
        }

        if 'masks' in output:
            masks = output['masks'].cpu()[keep]
            # 二值化Mask
            masks = (masks > self.mask_threshold).float()
            result['masks'] = masks

        return result

    def get_class_name(self, label):
        """获取类别名称"""
        class_names = {
            0: '背景',
            1: '松材线虫病',
            2: '其他病变'
        }
        return class_names.get(label.item() if isinstance(label, torch.Tensor) else label, '未知')


if __name__ == '__main__':
    # 测试Mask R-CNN模型
    print("=" * 60)
    print("测试Mask R-CNN模型")
    print("=" * 60)

    model = build_mask_rcnn(num_classes=2, pretrained=True)
    print(f"模型构建成功")

    # 计算参数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"总参数量: {total_params:,}")
    print(f"可训练参数量: {trainable_params:,}")

    # 测试推理
    model.eval()
    x = [torch.randn(3, 512, 512)]
    with torch.no_grad():
        outputs = model(x)
    print(f"输出keys: {outputs[0].keys()}")
    print(f"检测框数量: {outputs[0]['boxes'].shape[0]}")
