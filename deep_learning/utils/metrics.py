"""
CT图像松材线虫病检测系统 - 评估指标模块
"""
import numpy as np
import torch


def compute_dice(pred, target, smooth=1.0):
    """计算Dice系数"""
    pred = pred.flatten()
    target = target.flatten()
    intersection = (pred * target).sum()
    return (2.0 * intersection + smooth) / (pred.sum() + target.sum() + smooth)


def compute_iou(pred, target, smooth=1.0):
    """计算IoU (交并比)"""
    pred = pred.flatten()
    target = target.flatten()
    intersection = (pred * target).sum()
    union = pred.sum() + target.sum() - intersection
    return (intersection + smooth) / (union + smooth)


def compute_precision(pred, target, smooth=1.0):
    """计算精确率"""
    pred = pred.flatten()
    target = target.flatten()
    tp = (pred * target).sum()
    return (tp + smooth) / (pred.sum() + smooth)


def compute_recall(pred, target, smooth=1.0):
    """计算召回率"""
    pred = pred.flatten()
    target = target.flatten()
    tp = (pred * target).sum()
    return (tp + smooth) / (target.sum() + smooth)


def compute_f1(precision, recall):
    """计算F1分数"""
    return 2 * precision * recall / (precision + recall + 1e-8)


def compute_accuracy(pred, target):
    """计算像素级准确率"""
    return (pred == target).sum() / pred.numel()


def compute_hausdorff(pred, target):
    """计算Hausdorff距离（简化版）"""
    from scipy.ndimage import distance_transform_edt
    pred_np = pred.cpu().numpy().astype(bool) if torch.is_tensor(pred) else pred.astype(bool)
    target_np = target.cpu().numpy().astype(bool) if torch.is_tensor(target) else target.astype(bool)

    if not pred_np.any() or not target_np.any():
        return float('inf')

    # 计算从pred到target的距离
    dt_target = distance_transform_edt(~target_np)
    dt_pred = distance_transform_edt(~pred_np)

    # Hausdorff距离
    hd1 = dt_target[pred_np].max()
    hd2 = dt_pred[target_np].max()

    return max(hd1, hd2)


def evaluate_segmentation(pred, target, num_classes=2):
    """
    综合评估分割结果

    返回包含以下指标的字典:
    - dice: Dice系数
    - iou: 交并比
    - precision: 精确率
    - recall: 召回率
    - f1: F1分数
    - accuracy: 像素级准确率
    """
    if torch.is_tensor(pred):
        pred = pred.cpu().numpy()
    if torch.is_tensor(target):
        target = target.cpu().numpy()

    results = {}

    # 对每个类别（跳过背景）计算指标
    for cls in range(1, num_classes):
        pred_cls = (pred == cls).astype(np.float32)
        target_cls = (target == cls).astype(np.float32)

        dice = compute_dice(pred_cls, target_cls)
        iou = compute_iou(pred_cls, target_cls)
        precision = compute_precision(pred_cls, target_cls)
        recall = compute_recall(pred_cls, target_cls)
        f1 = compute_f1(precision, recall)
        accuracy = compute_accuracy(
            torch.from_numpy(pred_cls), torch.from_numpy(target_cls)
        )

        results[f'class{cls}'] = {
            'dice': float(dice),
            'iou': float(iou),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'accuracy': float(accuracy),
        }

    # 总体指标
    overall_acc = (pred == target).mean()
    results['overall_accuracy'] = float(overall_acc)

    return results


def compute_metrics_table(all_results):
    """生成模型对比表格"""
    import pandas as pd

    rows = []
    for model_name, results in all_results.items():
        row = {'Model': model_name}
        for cls_key, metrics in results.items():
            if isinstance(metrics, dict):
                for metric_name, value in metrics.items():
                    row[f'{cls_key}_{metric_name}'] = f'{value:.4f}'
        rows.append(row)

    df = pd.DataFrame(rows)
    return df
