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
| 前端 | Vue3 + Element Plus + ECharts + Axios |
| 后端 | SpringBoot 2.7 + MyBatis Plus + MySQL |
| 深度学习 | PyTorch + torchvision + ultralytics |
| 推理服务 | Flask (Python REST API) |
| 模型 | Improved U-Net / Standard U-Net / Mask R-CNN / YOLOv8/v10/v11 |

## 项目结构

```
ct-pine-wilt-detection/
├── frontend/                    # Vue3前端
│   ├── src/
│   │   ├── api/                # Axios API封装
│   │   ├── router/             # Vue Router路由
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
│   │   ├── controller/          # 控制器
│   │   ├── entity/              # 实体类
│   │   ├── mapper/              # MyBatis Mapper
│   │   ├── service/             # 服务接口
│   │   │   └── impl/            # 服务实现
│   │   └── util/                # 工具类
│   ├── src/main/resources/
│   │   └── application.yml     # 配置文件
│   ├── sql/
│   │   └── init.sql             # 数据库建表脚本
│   └── pom.xml
│
└── deep_learning/               # 深度学习模块
    ├── models/
    │   ├── improved_unet.py     # 改进U-Net模型
    │   ├── mask_rcnn.py         # Mask R-CNN模型
    │   ├── yolo_model.py        # YOLO模型
    │   └── losses.py            # 损失函数
    ├── data/
    │   └── dataset.py           # 数据集处理
    ├── utils/
    │   └── metrics.py           # 评估指标
    ├── config.py                # 全局配置
    ├── train_unet.py            # U-Net训练脚本
    ├── train_all_models.py      # 多模型训练对比
    └── app.py                   # Flask推理服务
```

## 快速开始

### 1. 环境准备

```bash
# Python环境
pip install torch torchvision flask flask-cors opencv-python numpy pillow albumentations ultralytics

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

## 模型训练

### 训练改进U-Net

```bash
cd deep_learning
python train_unet.py --model improved --epochs 100 --batch_size 8
```

### 训练标准U-Net (对比基线)

```bash
python train_unet.py --model standard --epochs 100 --batch_size 8
```

### 训练Mask R-CNN

```bash
python -c "from models.mask_rcnn import PineWiltMaskRCNN; ..."
```

### 训练YOLO

```bash
python -c "from models.yolo_model import PineWiltYOLO; ..."
```

### 多模型对比

```bash
python train_all_models.py
```

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| user | user123 | 普通用户 |

## 作者

刘昕月 (学号: 2022222997)
