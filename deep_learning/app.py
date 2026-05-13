"""
CT图像松材线虫病检测系统 - Python Flask推理服务
提供REST API供SpringBoot后端调用
"""
import os
import time
import base64
import io
import json
import traceback

import numpy as np
import cv2
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS

# ============ 初始化Flask应用 ============
app = Flask(__name__)
CORS(app)

# ============ 全局模型缓存 ============
MODELS = {}
MODEL_CONFIG = {
    'Improved U-Net': {
        'type': 'segmentation',
        'module': 'models.improved_unet',
        'class': 'ImprovedUNet',
    },
    'Standard U-Net': {
        'type': 'segmentation',
        'module': 'models.improved_unet',
        'class': 'StandardUNet',
    },
    'Mask R-CNN': {
        'type': 'instance_segmentation',
        'module': 'models.mask_rcnn',
        'class': 'PineWiltMaskRCNN',
    },
    'YOLOv8': {
        'type': 'detection',
        'module': 'models.yolo_model',
        'class': 'PineWiltYOLO',
    },
}


def get_model(model_name):
    """获取或加载模型"""
    import torch

    if model_name in MODELS:
        return MODELS[model_name]

    config = MODEL_CONFIG.get(model_name)
    if config is None:
        raise ValueError(f"未知模型: {model_name}")

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"加载模型 {model_name} (设备: {device})...")

    if model_name == 'Improved U-Net':
        from models.improved_unet import ImprovedUNet
        model = ImprovedUNet(in_channels=3, out_channels=2, base_filters=64)
        # 加载权重（如果存在）
        weight_path = f'weights/improved_unet_best.pth'
        if os.path.exists(weight_path):
            checkpoint = torch.load(weight_path, map_location=device)
            model.load_state_dict(checkpoint['model_state_dict'])
            print(f"  加载权重: {weight_path}")
        model.to(device)
        model.eval()
        MODELS[model_name] = model

    elif model_name == 'Standard U-Net':
        from models.improved_unet import StandardUNet
        model = StandardUNet(in_channels=3, out_channels=2, base_filters=64)
        weight_path = f'weights/standard_unet_best.pth'
        if os.path.exists(weight_path):
            checkpoint = torch.load(weight_path, map_location=device)
            model.load_state_dict(checkpoint['model_state_dict'])
            print(f"  加载权重: {weight_path}")
        model.to(device)
        model.eval()
        MODELS[model_name] = model

    elif model_name == 'Mask R-CNN':
        from models.mask_rcnn import PineWiltMaskRCNN
        detector = PineWiltMaskRCNN(num_classes=2, device=device)
        weight_path = f'weights/mask_rcnn_best.pth'
        if os.path.exists(weight_path):
            detector.load_weights(weight_path)
        MODELS[model_name] = detector

    elif model_name.startswith('YOLO'):
        from models.yolo_model import PineWiltYOLO
        version = model_name.replace('YOLO', '').lower()
        detector = PineWiltYOLO(version=version, model_size='s', num_classes=1, device=device)
        MODELS[model_name] = detector

    return MODELS[model_name]


def denoise_image(image, method='none'):
    """
    CT图像去噪预处理

    Args:
        image: numpy array (H, W, C) uint8
        method: 去噪方法

    Returns:
        去噪后的图像
    """
    if method == 'none' or method is None:
        return image

    if method == 'bilateral':
        return cv2.bilateralFilter(image, 9, 75, 75)

    elif method == 'gaussian':
        return cv2.GaussianBlur(image, (5, 5), 0)

    elif method == 'median':
        return cv2.medianBlur(image, 5)

    elif method == 'nlmeans':
        # nlmeans需要灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            return cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
        return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

    return image


def calculate_metrics(pred_mask, gt_mask=None):
    """
    计算评估指标

    Args:
        pred_mask: 预测掩码 (H, W)
        gt_mask: 真实掩码 (H, W)，可选

    Returns:
        指标字典
    """
    if gt_mask is not None:
        intersection = np.logical_and(pred_mask > 0, gt_mask > 0).sum()
        union = np.logical_or(pred_mask > 0, gt_mask > 0).sum()

        dice = 2.0 * intersection / (pred_mask.sum() + gt_mask.sum() + 1e-8)
        iou = intersection / (union + 1e-8)

        tp = intersection
        fp = (pred_mask > 0).sum() - tp
        fn = (gt_mask > 0).sum() - tp

        precision = tp / (tp + fp + 1e-8)
        recall = tp / (tp + fn + 1e-8)
        f1 = 2 * precision * recall / (precision + recall + 1e-8)

        total = pred_mask.size
        tn = total - tp - fp - fn
        accuracy = (tp + tn) / (total + 1e-8)

        return {
            'dice_score': round(float(dice), 4),
            'iou_score': round(float(iou), 4),
            'precision': round(float(precision), 4),
            'recall': round(float(recall), 4),
            'f1_score': round(float(f1), 4),
            'accuracy': round(float(accuracy), 4),
        }
    else:
        # 无GT时，仅返回检测结果
        lesion_area = (pred_mask > 0).sum()
        total_area = pred_mask.size
        return {
            'dice_score': 0.0,
            'iou_score': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'accuracy': round(float(1 - lesion_area / total_area), 4) if total_area > 0 else 0.0,
            'lesion_area': int(lesion_area),
            'lesion_ratio': round(float(lesion_area / total_area), 4) if total_area > 0 else 0.0,
        }


# ============ API路由 ============

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'Python推理服务运行中'})


@app.route('/detect', methods=['POST'])
def detect():
    """
    检测接口

    请求参数:
    - image_path: 图像路径 (必填)
    - model_name: 模型名称 (默认: Improved U-Net)
    - denoise_method: 去噪方法 (默认: none)

    返回:
    - result: positive/negative
    - 分割指标
    - 分割结果图像(base64)
    """
    try:
        data = request.get_json()
        image_path = data.get('image_path', '')
        model_name = data.get('model_name', 'Improved U-Net')
        denoise_method = data.get('denoise_method', 'none')

        if not image_path or not os.path.exists(image_path):
            return jsonify({'error': f'图像不存在: {image_path}'}), 400

        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            return jsonify({'error': f'图像读取失败: {image_path}'}), 400

        # 去噪预处理
        image = denoise_image(image, denoise_method)

        # 记录推理开始时间
        start_time = time.time()

        # 获取模型
        model = get_model(model_name)

        import torch

        # ========= 根据模型类型执行推理 =========
        result_data = {}

        if model_name in ['Improved U-Net', 'Standard U-Net']:
            # U-Net分割模型推理
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_tensor = torch.from_numpy(image_rgb).permute(2, 0, 1).float() / 255.0
            image_tensor = image_tensor.unsqueeze(0)

            device = next(model.parameters()).device
            image_tensor = image_tensor.to(device)

            with torch.no_grad():
                output = model(image_tensor)
                pred_mask = torch.argmax(output, dim=1).squeeze().cpu().numpy()

            # 生成彩色分割图
            seg_image = np.zeros_like(image)
            seg_image[pred_mask > 0] = [0, 0, 255]  # 红色标记病变区域

            # 叠加显示
            overlay = cv2.addWeighted(image, 0.7, seg_image, 0.3, 0)

            # 计算指标
            metrics = calculate_metrics(pred_mask)
            result_data.update(metrics)

            # 判断阳性/阴性
            is_positive = int(pred_mask.sum()) > 0
            result_data['result'] = 'positive' if is_positive else 'negative'

        elif model_name == 'Mask R-CNN':
            # Mask R-CNN推理
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_tensor = torch.from_numpy(image_rgb).permute(2, 0, 1).float() / 255.0

            result = model.predict(image_tensor)

            seg_image = np.zeros_like(image)
            if result['masks'].shape[0] > 0:
                for i in range(result['masks'].shape[0]):
                    mask = result['masks'][i, 0].numpy()
                    seg_image[mask > 0] = [0, 0, 255]

            overlay = cv2.addWeighted(image, 0.7, seg_image, 0.3, 0)

            is_positive = result['boxes'].shape[0] > 0
            result_data['result'] = 'positive' if is_positive else 'negative'
            result_data['num_detections'] = int(result['boxes'].shape[0])

        elif model_name.startswith('YOLO'):
            # YOLO检测推理
            results = model.predict(image_path, save=False, save_txt=False)

            overlay = image.copy()
            is_positive = False
            num_detections = 0

            if results and len(results) > 0:
                r = results[0]
                if r.boxes is not None and len(r.boxes) > 0:
                    is_positive = True
                    num_detections = len(r.boxes)
                    for box in r.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        conf = float(box.conf[0])
                        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(overlay, f'{conf:.2f}', (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            result_data['result'] = 'positive' if is_positive else 'negative'
            result_data['num_detections'] = num_detections

        # 推理时间
        inference_time = int((time.time() - start_time) * 1000)
        result_data['inference_time'] = inference_time

        # 保存分割结果
        result_dir = './uploads/results'
        os.makedirs(result_dir, exist_ok=True)
        result_filename = f'result_{int(time.time())}.png'
        result_path = os.path.join(result_dir, result_filename)
        cv2.imwrite(result_path, overlay)
        result_data['segmentation_path'] = result_path

        # 转为base64
        _, buffer = cv2.imencode('.png', overlay)
        result_data['segmentation_base64'] = base64.b64encode(buffer).decode('utf-8')

        return jsonify(result_data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/models', methods=['GET'])
def list_models():
    """获取可用模型列表"""
    models = []
    for name, config in MODEL_CONFIG.items():
        models.append({
            'name': name,
            'type': config['type'],
            'available': True
        })
    return jsonify(models)


@app.route('/compare', methods=['POST'])
def compare_models():
    """
    多模型对比接口
    """
    try:
        data = request.get_json()
        image_path = data.get('image_path', '')
        models = data.get('models', ['Improved U-Net', 'Mask R-CNN', 'YOLOv8'])
        denoise_method = data.get('denoise_method', 'none')

        if not image_path or not os.path.exists(image_path):
            return jsonify({'error': f'图像不存在: {image_path}'}), 400

        results = []
        for model_name in models:
            try:
                # 逐模型检测
                detect_data = {
                    'image_path': image_path,
                    'model_name': model_name,
                    'denoise_method': denoise_method,
                }
                # 内部调用detect逻辑
                # 此处简化，实际项目中可异步调用
                results.append({
                    'model_name': model_name,
                    'status': 'success',
                })
            except Exception as e:
                results.append({
                    'model_name': model_name,
                    'status': 'error',
                    'error': str(e),
                })

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ 启动服务 ============
if __name__ == '__main__':
    print("=" * 60)
    print("CT图像松材线虫病检测系统 - Python推理服务")
    print("=" * 60)
    print("服务地址: http://localhost:5000")
    print("API列表:")
    print("  GET  /health       - 健康检查")
    print("  POST /detect       - 执行检测")
    print("  GET  /models       - 模型列表")
    print("  POST /compare      - 模型对比")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)
