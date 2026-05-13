"""
CT图像松材线虫病检测系统 - 损失函数模块
包含混合损失函数 (Dice Loss + Cross Entropy Loss)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceLoss(nn.Module):
    """
    Dice损失函数 - 用于优化病变区域的像素级匹配度
    解决数据不平衡导致的模型偏向正常组织预测问题
    """

    def __init__(self, smooth=1.0):
        super(DiceLoss, self).__init__()
        self.smooth = smooth

    def forward(self, predictions, targets):
        # predictions: [B, C, H, W], targets: [B, H, W]
        num_classes = predictions.shape[1]
        predictions = F.softmax(predictions, dim=1)

        total_loss = 0.0
        for cls in range(1, num_classes):  # 跳过背景类
            pred_cls = predictions[:, cls, :, :]
            target_cls = (targets == cls).float()

            intersection = (pred_cls * target_cls).sum(dim=(1, 2))
            union = pred_cls.sum(dim=(1, 2)) + target_cls.sum(dim=(1, 2))

            dice = (2.0 * intersection + self.smooth) / (union + self.smooth)
            total_loss += 1.0 - dice.mean()

        return total_loss / (num_classes - 1)


class CombinedLoss(nn.Module):
    """
    混合损失函数: Dice Loss + Cross Entropy Loss
    - Dice损失用于优化病变区域的像素级匹配度
    - 交叉熵损失用于优化整体分类精度
    两者结合使模型在小病变与整体分割上均有优异表现
    """

    def __init__(self, dice_weight=0.5, ce_weight=0.5, num_classes=2):
        super(CombinedLoss, self).__init__()
        self.dice_weight = dice_weight
        self.ce_weight = ce_weight
        self.dice_loss = DiceLoss()
        self.ce_loss = nn.CrossEntropyLoss(weight=torch.tensor([0.3, 0.7]))  # 加权CE

    def forward(self, predictions, targets):
        dice = self.dice_loss(predictions, targets)
        ce = self.ce_loss(predictions, targets)
        total_loss = self.dice_weight * dice + self.ce_weight * ce
        return total_loss, {'dice_loss': dice.item(), 'ce_loss': ce.item()}


class FocalLoss(nn.Module):
    """
    Focal Loss - 专注于难分类样本
    适用于病变区域占比较小的情况
    """

    def __init__(self, alpha=0.25, gamma=2.0, num_classes=2):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.num_classes = num_classes

    def forward(self, predictions, targets):
        ce_loss = F.cross_entropy(predictions, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()


class BCEDiceLoss(nn.Module):
    """BCE + Dice 组合损失"""

    def __init__(self, bce_weight=0.5, dice_weight=0.5):
        super(BCEDiceLoss, self).__init__()
        self.bce_weight = bce_weight
        self.dice_weight = dice_weight

    def forward(self, predictions, targets):
        # 二值化目标
        if predictions.shape[1] == 1:
            pred = torch.sigmoid(predictions).squeeze(1)
        else:
            pred = F.softmax(predictions, dim=1)[:, 1, :, :]

        if targets.dim() == 3:
            target_bin = (targets > 0).float()
        else:
            target_bin = targets.float()

        # BCE
        bce = F.binary_cross_entropy(pred, target_bin)

        # Dice
        smooth = 1.0
        intersection = (pred * target_bin).sum(dim=(1, 2))
        union = pred.sum(dim=(1, 2)) + target_bin.sum(dim=(1, 2))
        dice = (2.0 * intersection + smooth) / (union + smooth)
        dice_loss = 1.0 - dice.mean()

        return self.bce_weight * bce + self.dice_weight * dice_loss
