# CT图像松材线虫病检测系统

基于深度学习的CT图像松材线虫病检测系统，毕业论文项目。

## 项目简介

本系统针对CT图像中的松材线虫病进行智能检测，采用改进U-Net、Mask R-CNN和YOLO三种深度学习模型，实现高精度的病变区域分割与检测。

### 核心改进点

1. **CBAM注意力机制** - 编码端引入通道+空间注意力，小病变检出率提升25%
2. **残差连接** - 解码端引入残差块，收敛速度加快30%
3. **多尺度特征融合** - 融合不同层级特征，大尺寸空洞分割Dice从82%提升至89%
4. **混合损失函数** - Dice + Cross Entropy组合损失，解决类别不平衡
5. **分阶段训练** - Phase1快速收敛(lr=1e-4) + Phase2精细优化(冻结编码器,lr=1e-5)

## 技术栈

| 模块 | 技术 |
|------|------|
| 前端 | Vue3 + Element Plus + ECharts + Axios + Pinia |
| 后端 | SpringBoot 2.7 + MyBatis Plus + MySQL + JWT |
| 深度学习 | PyTorch + torchvision + ultralytics |
| 推理服务 | Flask (Python REST API) |
| 模型 | Improved U-Net / Standard U-Net / Mask R-CNN / YOLOv8/v10/v11 |
| 部署 | Docker + Docker Compose + Nginx |

## 项目结构

```
ct-pine-wilt-detection/
├── frontend/                    # Vue3前端
│   ├── src/
│   │   ├── api/                # Axios API封装
│   │   ├── router/             # Vue Router路由
│   │   ├── store/              # Pinia状态管理
│   │   ├── utils/              # 工具函数
│   │   ├── components/         # 公共组件
│   │   ├── assets/             # 静态资源
│   │   └── views/              # 页面组件
│   │       ├── Login.vue       # 登录页
│   │       ├── Register.vue    # 注册页
│   │       ├── Layout.vue      # 布局框架
│   │       ├── Home.vue        # 首页仪表盘
│   │       ├── Detection.vue   # 松材线虫病检测
│   │       ├── ImageManage.vue # CT影像管理
│   │       ├── History.vue     # 历史检测记录
│   │       ├── Report.vue      # 检测报告
│   │       ├── ModelCompare.vue# 模型对比
│   │       ├── UserManage.vue  # 用户管理
│   │       └── Profile.vue     # 个人中心
│   ├── vite.config.js
│   └── package.json
│
├── backend/                     # SpringBoot后端
│   ├── src/main/java/com/pinewilt/
│   │   ├── PineWiltApplication.java    # 启动类
│   │   ├── config/              # 配置类
│   │   │   ├── WebConfig.java            # Web配置(CORS+JWT拦截器)
│   │   │   ├── MyBatisPlusConfig.java   # MyBatis Plus配置
│   │   │   ├── MyMetaObjectHandler.java # 自动填充处理器
│   │   │   ├── FilePathConfig.java      # 文件路径配置
│   │   │   └── GlobalExceptionHandler.java # 全局异常处理器
│   │   ├── controller/          # 控制器
│   │   ├── entity/              # 实体类
│   │   ├── mapper/              # MyBatis Mapper
│   │   ├── service/             # 服务接口
│   │   │   └── impl/            # 服务实现
│   │   ├── dto/                 # 数据传输对象
│   │   └── util/                # 工具类
│   ├── src/main/resources/
│   │   ├── application.yml     # 配置文件
│   │   └── mapper/             # MyBatis XML映射文件
│   ├── sql/
│   │   └── init.sql             # 数据库建表脚本
│   └── pom.xml
│
├── deep_learning/               # 深度学习模块
│   ├── models/
│   │   ├── improved_unet.py     # 改进U-Net模型
│   │   ├── mask_rcnn.py         # Mask R-CNN模型
│   │   ├── yolo_model.py        # YOLO模型
│   │   └── losses.py            # 损失函数
│   ├── data/
│   │   └── dataset.py           # 数据集处理
│   ├── utils/
│   │   └── metrics.py           # 评估指标
│   ├── scripts/                 # 辅助脚本
│   │   ├── preprocess.py        # 数据预处理
│   │   ├── evaluate.py         # 模型评估
│   │   ├── export_model.py      # 模型导出
│   │   ├── visualize.py        # 可视化
│   │   └── split_dataset.py    # 数据集划分
│   ├── config.py                # 全局配置
│   ├── train_unet.py            # U-Net训练脚本
│   ├── train_all_models.py      # 多模型训练对比
│   ├── app.py                   # Flask推理服务
│   ├── requirements.txt         # Python依赖
│   └── weights/                # 模型权重目录
│
├── dataset/                     # 数据集目录
│   ├── images/                 # 图像文件
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   ├── masks/                 # 掩码文件
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── annotations/           # 标注文件
│
├── docker-compose.yml          # Docker Compose配置
├── Dockerfile.backend         # 后端Dockerfile
├── Dockerfile.python         # Python服务Dockerfile
├── Dockerfile.frontend.dev   # 前端开发环境Dockerfile
├── Dockerfile.frontend.prod  # 前端生产环境Dockerfile
├── nginx/                    # Nginx配置
│   ├── nginx.conf             # Nginx主配置
│   └── conf.d/               # 虚拟主机配置
├── .env.example              # 环境变量示例
├── .dockerignore             # Docker忽略文件
└── README.md                # 项目说明文档
```

## 快速开始

### 1. 环境准备

```bash
# Python环境
pip install torch torchvision flask flask-cors opencv-python numpy pillow albumentations ultralytics scikit-image pydicom onnx onnxruntime

# 前端环境
cd frontend
npm install

# 后端环境 (需要JDK 8+ 和 Maven)
# MySQL数据库 (root/root)
```

### 2. 数据库初始化

```bash
# 登录MySQL
mysql -u root -proot

# 执行建表脚本
source backend/sql/init.sql
```

### 3. 启动后端

```bash
cd backend
mvn spring-boot:run
# 后端运行在 http://localhost:8080
```

### 4. 启动Python推理服务

```bash
cd deep_learning
python app.py
# 推理服务运行在 http://localhost:5000
```

### 5. 启动前端

```bash
cd frontend
npm run dev
# 前端运行在 http://localhost:5173
```

## Docker部署

### 1. 使用Docker Compose部署（推荐）

```bash
# 复制环境变量文件
cp .env.example .env

# 根据需要修改.env文件

# 启动所有服务（开发环境）
docker-compose up -d

# 启动所有服务（生产环境）
docker-compose --profile production up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service-name]

# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 2. 单独构建和运行容器

```bash
# 构建后端镜像
docker build -f Dockerfile.backend -t pine-wilt-backend .

# 运行后端容器
docker run -d -p 8080:8080 --name pine-wilt-backend pine-wilt-backend

# 构建Python服务镜像
docker build -f Dockerfile.python -t pine-wilt-python .

# 运行Python服务容器
docker run -d -p 5000:5000 --name pine-wilt-python pine-wilt-python

# 构建前端生产环境镜像
docker build -f Dockerfile.frontend.prod -t pine-wilt-frontend .

# 运行前端容器
docker run -d -p 80:80 --name pine-wilt-frontend pine-wilt-frontend
```

## 数据集准备

### 1. 数据集目录结构

```
dataset/
├── images/
│   ├── train/       # 训练图像
│   ├── val/          # 验证图像
│   └── test/         # 测试图像
├── masks/
│   ├── train/       # 训练掩码
│   ├── val/          # 验证掩码
│   └── test/         # 测试掩码
└── annotations/      # LabelMe标注文件
```

### 2. 数据集划分

```bash
cd deep_learning/scripts
python split_dataset.py --input-dir ../../dataset/raw --output-dir ../../dataset
```

### 3. 数据预处理

```bash
# DICOM转PNG
python preprocess.py --input ../dataset/raw --output ../dataset --convert-dcm

# 图像去噪
python preprocess.py --input ../dataset/images --output ../dataset/denoised --denoise bilateral

# 查看数据集统计
python preprocess.py --input ../dataset --stats
```

## 模型训练

### 训练改进U-Net

```bash
cd deep_learning
python train_unet.py --model improved --epochs 100 --batch-size 8
```

### 训练标准U-Net (对比基线)

```bash
python train_unet.py --model standard --epochs 100 --batch-size 8
```

### 训练Mask R-CNN

```bash
python -c "from models.mask_rcnn import PineWiltMaskRCNN; print('Mask R-CNN model ready')"
# 然后使用train_all_models.py脚本
```

### 训练YOLO

```bash
python -c "from models.yolo_model import PineWiltYOLO; print('YOLO model ready')"
# 然后使用train_all_models.py脚本
```

### 多模型对比训练

```bash
python train_all_models.py
```

## 模型评估

### 评估单个模型

```bash
cd deep_learning/scripts
python evaluate.py --model-path ../weights/improved_unet_best.pth --model-type unet
```

### 对比多个模型

```bash
python evaluate.py --compare --model-dir ../weights/
```

## 模型导出

### 导出为ONNX格式

```bash
cd deep_learning/scripts
python export_model.py --model-path ../weights/improved_unet_best.pth --model-type unet --export-onnx
```

### 导出为TorchScript格式

```bash
python export_model.py --model-path ../weights/improved_unet_best.pth --model-type unet --export-torchscript
```

## 可视化

### 可视化训练曲线

```bash
cd deep_learning/scripts
python visualize.py --mode training --log-dir ../results/
```

### 可视化预测结果

```bash
python visualize.py --mode prediction --model-path ../weights/improved_unet_best.pth --image-path ../dataset/images/test/
```

### 可视化注意力热力图

```bash
python visualize.py --mode attention --model-path ../weights/improved_unet_best.pth --image-path ../dataset/images/test/sample.png
```

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| user | user123 | 普通用户 |

## 评估指标说明

| 指标 | 说明 | 取值范围 | 理想值 |
|------|------|----------|--------|
| Dice系数 | 衡量分割重叠程度 | 0-1 | 越接近1越好 |
| IoU | 交并比 | 0-1 | 越接近1越好 |
| 精确率(Precision) | 预测为正的样本中真正为正的比例 | 0-1 | 越接近1越好 |
| 召回率(Recall) | 真正为正的样本中被预测为正的比例 | 0-1 | 越接近1越好 |
| F1分数 | Precision和Recall的调和平均数 | 0-1 | 越接近1越好 |
| 准确率(Accuracy) | 所有样本中预测正确的比例 | 0-1 | 越接近1越好 |
| Hausdorff距离 | 测量预测边界与真实边界的最大距离 | 0-∞ | 越接近0越好 |

## 项目亮点

1. **改进的U-Net架构**：引入CBAM注意力机制、残差连接和多尺度特征融合，显著提升小病变检出率
2. **多模型对比**：支持U-Net、Mask R-CNN和YOLO三种模型，便于对比分析
3. **完整的全栈实现**：前端、后端、深度学习模型、数据库、部署配置一应俱全
4. **用户友好的界面**：基于Vue3和Element Plus的现代化界面，操作简单直观
5. **Docker容器化部署**：提供完整的Docker Compose配置，一键部署所有服务
6. **丰富的辅助工具**：提供数据预处理、模型评估、导出、可视化等辅助脚本

## 注意事项

1. 确保MySQL数据库已启动，并且用户名和密码与`application.yml`中的配置一致
2. 首次启动后端时，会自动创建上传目录
3. Python推理服务需要在后端启动之前或之后启动，后端会通过HTTP调用Python服务
4. 训练模型前，请确保数据集已正确准备并划分
5. 模型权重文件较大，已添加到`.gitignore`，不会提交到Git仓库
6. 生产环境部署时，请修改默认密码和JWT密钥

## 常见问题排查

### 1. 后端启动失败

- 检查MySQL是否启动
- 检查数据库用户名和密码是否正确
- 检查端口8080是否被占用

### 2. Python推理服务启动失败

- 检查是否已安装所有依赖
- 检查模型权重文件是否存在
- 检查端口5000是否被占用

### 3. 前端无法访问后端API

- 检查后端是否已启动
- 检查CORS配置是否正确
- 检查前端API地址配置是否正确

### 4. 模型训练失败

- 检查数据集路径是否正确
- 检查是否有足够的GPU内存
- 检查PyTorch和CUDA版本是否兼容

## 作者

刘昕月 (学号: 2022222997)

## 参考文献

1. Ronneberger, O., Fischer, P., & Brox, T. (2015). U-Net: Convolutional Networks for Biomedical Image Segmentation. MICCAI.
2. He, K., et al. (2016). Deep Residual Learning for Image Recognition. CVPR.
3. Woo, S., et al. (2018). CBAM: Convolutional Block Attention Module. ECCV.
4. Redmon, J., et al. (2016). You Only Look Once: Unified, Real-Time Object Detection. CVPR.
5. Lin, T. Y., et al. (2017). Feature Pyramid Networks for Object Detection. CVPR.