"""
CT图像松材线虫病检测系统 - YOLO模型
支持YOLOv8/v10/v11版本的松材线虫病检测
"""
import torch
import torch.nn as nn
import os
import sys


def build_yolov8(num_classes=1, model_size='s', pretrained=True):
    """
    构建YOLOv8模型

    Args:
        num_classes: 检测类别数 (不含背景)
        model_size: 模型大小 n/s/m/l/x
        pretrained: 是否使用预训练权重

    Returns:
        model: YOLOv8模型
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("请安装ultralytics: pip install ultralytics")
        return None

    size_map = {
        'n': 'yolov8n',
        's': 'yolov8s',
        'm': 'yolov8m',
        'l': 'yolov8l',
        'x': 'yolov8x',
    }

    model_name = size_map.get(model_size, 'yolov8s')

    if pretrained:
        model = YOLO(f'{model_name}.pt')
    else:
        model = YOLO(f'{model_name}.yaml')

    # 设置类别数
    model.overrides['nc'] = num_classes

    return model


def build_yolov10(num_classes=1, model_size='s', pretrained=True):
    """
    构建YOLOv10模型

    Args:
        num_classes: 检测类别数 (不含背景)
        model_size: 模型大小 n/s/m/l/x
        pretrained: 是否使用预训练权重

    Returns:
        model: YOLOv10模型
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("请安装ultralytics: pip install ultralytics")
        return None

    size_map = {
        'n': 'yolov10n',
        's': 'yolov10s',
        'm': 'yolov10m',
        'l': 'yolov10l',
        'x': 'yolov10x',
    }

    model_name = size_map.get(model_size, 'yolov10s')

    if pretrained:
        model = YOLO(f'{model_name}.pt')
    else:
        model = YOLO(f'{model_name}.yaml')

    model.overrides['nc'] = num_classes

    return model


def build_yolov11(num_classes=1, model_size='s', pretrained=True):
    """
    构建YOLOv11模型

    Args:
        num_classes: 检测类别数 (不含背景)
        model_size: 模型大小 n/s/m/l/x
        pretrained: 是否使用预训练权重

    Returns:
        model: YOLOv11模型
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("请安装ultralytics: pip install ultralytics")
        return None

    size_map = {
        'n': 'yolo11n',
        's': 'yolo11s',
        'm': 'yolo11m',
        'l': 'yolo11l',
        'x': 'yolo11x',
    }

    model_name = size_map.get(model_size, 'yolo11s')

    if pretrained:
        model = YOLO(f'{model_name}.pt')
    else:
        model = YOLO(f'{model_name}.yaml')

    model.overrides['nc'] = num_classes

    return model


class PineWiltYOLO:
    """
    松材线虫病YOLO检测器
    封装YOLOv8/v10/v11的训练、推理和评估
    """

    # 类别名称映射
    CLASS_NAMES = {
        0: 'pine_wilt_disease',    # 松材线虫病
    }

    def __init__(self, version='v8', model_size='s', num_classes=1,
                 device='cuda', conf_threshold=0.5, iou_threshold=0.45):
        """
        Args:
            version: YOLO版本 'v8'/'v10'/'v11'
            model_size: 模型大小 n/s/m/l/x
            num_classes: 检测类别数
            device: 计算设备
            conf_threshold: 置信度阈值
            iou_threshold: IoU阈值
        """
        self.version = version
        self.model_size = model_size
        self.num_classes = num_classes
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

        # 构建模型
        if version == 'v8':
            self.model = build_yolov8(num_classes, model_size)
        elif version == 'v10':
            self.model = build_yolov10(num_classes, model_size)
        elif version == 'v11':
            self.model = build_yolov11(num_classes, model_size)
        else:
            raise ValueError(f"不支持的YOLO版本: {version}")

    def train(self, data_yaml, epochs=100, batch_size=16, imgsz=640,
              lr0=0.01, patience=50, project='runs/train', name='pine_wilt'):
        """
        训练YOLO模型

        Args:
            data_yaml: 数据集配置文件路径 (YOLO格式)
            epochs: 训练轮数
            batch_size: 批次大小
            imgsz: 输入图像大小
            lr0: 初始学习率
            patience: 早停耐心值
            project: 结果保存目录
            name: 实验名称

        Returns:
            results: 训练结果
        """
        if self.model is None:
            print("模型未正确加载")
            return None

        results = self.model.train(
            data=data_yaml,
            epochs=epochs,
            batch=batch_size,
            imgsz=imgsz,
            lr0=lr0,
            patience=patience,
            device=self.device,
            project=project,
            name=name,
            exist_ok=True,
            verbose=True,
        )

        return results

    def predict(self, source, save=True, save_txt=True, conf=None):
        """
        执行推理

        Args:
            source: 输入源 (图像路径/目录/摄像头)
            save: 是否保存结果
            save_txt: 是否保存检测框标签
            conf: 置信度阈值 (None则使用默认值)

        Returns:
            results: 推理结果
        """
        if self.model is None:
            print("模型未正确加载")
            return None

        conf = conf or self.conf_threshold

        results = self.model.predict(
            source=source,
            conf=conf,
            iou=self.iou_threshold,
            device=self.device,
            save=save,
            save_txt=save_txt,
            verbose=False,
        )

        return results

    def validate(self, data_yaml=None, split='test'):
        """
        验证模型

        Args:
            data_yaml: 数据集配置文件
            split: 验证集分割

        Returns:
            metrics: 评估指标
        """
        if self.model is None:
            print("模型未正确加载")
            return None

        metrics = self.model.val(
            data=data_yaml,
            split=split,
            device=self.device,
            verbose=True,
        )

        return metrics

    def load_weights(self, weight_path):
        """
        加载训练好的权重

        Args:
            weight_path: 权重文件路径
        """
        try:
            from ultralytics import YOLO
            self.model = YOLO(weight_path)
            print(f"权重已加载: {weight_path}")
        except Exception as e:
            print(f"加载权重失败: {e}")

    def export(self, format='onnx', **kwargs):
        """
        导出模型

        Args:
            format: 导出格式 (onnx/torchscript/engine等)
        """
        if self.model is None:
            print("模型未正确加载")
            return

        self.model.export(format=format, **kwargs)
        print(f"模型已导出为 {format} 格式")


def create_yolo_dataset_yaml(output_path, train_dir, val_dir, test_dir=None,
                              class_names=None):
    """
    创建YOLO格式的数据集配置文件

    Args:
        output_path: 输出YAML文件路径
        train_dir: 训练集图像目录
        val_dir: 验证集图像目录
        test_dir: 测试集图像目录
        class_names: 类别名称列表
    """
    import yaml

    if class_names is None:
        class_names = ['pine_wilt_disease']

    data = {
        'path': os.path.dirname(output_path),
        'train': train_dir,
        'val': val_dir,
        'names': {i: name for i, name in enumerate(class_names)}
    }

    if test_dir:
        data['test'] = test_dir

    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    print(f"数据集配置文件已创建: {output_path}")


def convert_labelme_to_yolo(labelme_dir, output_dir, class_mapping=None):
    """
    将LabelMe标注转换为YOLO格式

    Args:
        labelme_dir: LabelMe JSON文件目录
        output_dir: 输出目录
        class_mapping: 类别名称映射 {name: id}
    """
    import json
    import shutil
    from pathlib import Path

    if class_mapping is None:
        class_mapping = {
            'Vector insect': 0,
            'pine_wilt_disease': 0,
            'hsdoiaihod': 0,
        }

    labelme_path = Path(labelme_dir)
    output_path = Path(output_dir)

    # 创建输出目录
    (output_path / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (output_path / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (output_path / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (output_path / 'labels' / 'val').mkdir(parents=True, exist_ok=True)

    json_files = list(labelme_path.glob('*.json'))
    print(f"找到 {len(json_files)} 个LabelMe标注文件")

    # 80/20 分割
    split_idx = int(len(json_files) * 0.8)

    for idx, json_file in enumerate(json_files):
        split = 'train' if idx < split_idx else 'val'

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        img_width = data['imageWidth']
        img_height = data['imageHeight']

        # 获取图像文件路径
        img_file = labelme_path / data['imagePath']

        # 转换标注
        yolo_lines = []
        for shape in data['shapes']:
            label = shape['label']
            if label not in class_mapping:
                print(f"警告: 未知类别 '{label}'，跳过")
                continue

            class_id = class_mapping[label]

            if shape['shape_type'] == 'rectangle':
                # 矩形标注
                points = shape['points']
                x1, y1 = points[0]
                x2, y2 = points[1]

                # 转换为YOLO格式 (中心点归一化)
                cx = ((x1 + x2) / 2) / img_width
                cy = ((y1 + y2) / 2) / img_height
                w = abs(x2 - x1) / img_width
                h = abs(y2 - y1) / img_height

                yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

            elif shape['shape_type'] == 'polygon':
                # 多边形标注 - 使用外接矩形
                points = shape['points']
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]

                x1, x2 = min(xs), max(xs)
                y1, y2 = min(ys), max(ys)

                cx = ((x1 + x2) / 2) / img_width
                cy = ((y1 + y2) / 2) / img_height
                w = (x2 - x1) / img_width
                h = (y2 - y1) / img_height

                yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

        # 保存YOLO格式标注
        label_name = json_file.stem + '.txt'
        with open(output_path / 'labels' / split / label_name, 'w') as f:
            f.write('\n'.join(yolo_lines))

        # 复制图像
        if img_file.exists():
            shutil.copy2(
                img_file,
                output_path / 'images' / split / img_file.name
            )

    print(f"转换完成！训练集: {split_idx}, 验证集: {len(json_files) - split_idx}")


if __name__ == '__main__':
    # 测试YOLO模型构建
    print("=" * 60)
    print("测试YOLO模型构建")
    print("=" * 60)

    for version in ['v8', 'v10', 'v11']:
        print(f"\n构建 YOLO{version}...")
        try:
            detector = PineWiltYOLO(version=version, model_size='s', num_classes=1)
            if detector.model is not None:
                print(f"YOLO{version} 构建成功!")
            else:
                print(f"YOLO{version} 构建失败，请安装ultralytics")
        except Exception as e:
            print(f"YOLO{version} 构建异常: {e}")
