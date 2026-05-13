-- =============================================
-- CT图像松材线虫病检测系统 - 数据库建表脚本
-- =============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS pine_wilt_detection DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pine_wilt_detection;

-- 1. 用户表
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(100) NOT NULL COMMENT '密码',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `role` VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色(admin/user)',
    `status` VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态(active/inactive)',
    `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '逻辑删除(0-未删除/1-已删除)',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. CT影像表
DROP TABLE IF EXISTS `ct_image`;
CREATE TABLE `ct_image` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `image_name` VARCHAR(255) NOT NULL COMMENT '影像名称',
    `file_path` VARCHAR(500) NOT NULL COMMENT '文件路径',
    `file_size` VARCHAR(50) DEFAULT NULL COMMENT '文件大小',
    `format` VARCHAR(20) DEFAULT 'jpg' COMMENT '格式(jpg/png/dcm)',
    `width` INT DEFAULT NULL COMMENT '图像宽度',
    `height` INT DEFAULT NULL COMMENT '图像高度',
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态(pending/detected/processing)',
    `user_id` BIGINT DEFAULT NULL COMMENT '上传用户ID',
    `denoise_method` VARCHAR(20) DEFAULT 'none' COMMENT '去噪方法(none/bilateral/gaussian/median/nlmeans)',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '逻辑删除',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='CT影像表';

-- 3. 检测记录表
DROP TABLE IF EXISTS `detection_record`;
CREATE TABLE `detection_record` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `image_id` BIGINT NOT NULL COMMENT '影像ID',
    `image_name` VARCHAR(255) DEFAULT NULL COMMENT '影像名称',
    `model_name` VARCHAR(50) NOT NULL COMMENT '使用模型',
    `result` VARCHAR(20) NOT NULL COMMENT '检测结果(positive/negative)',
    `dice_score` DECIMAL(6,4) DEFAULT NULL COMMENT 'Dice系数',
    `iou_score` DECIMAL(6,4) DEFAULT NULL COMMENT 'IoU',
    `precision` DECIMAL(6,4) DEFAULT NULL COMMENT '精确率',
    `recall` DECIMAL(6,4) DEFAULT NULL COMMENT '召回率',
    `f1_score` DECIMAL(6,4) DEFAULT NULL COMMENT 'F1分数',
    `accuracy` DECIMAL(6,4) DEFAULT NULL COMMENT '准确率',
    `hausdorff` DECIMAL(10,2) DEFAULT NULL COMMENT 'Hausdorff距离',
    `segmentation_path` VARCHAR(500) DEFAULT NULL COMMENT '分割结果路径',
    `original_image_path` VARCHAR(500) DEFAULT NULL COMMENT '原始影像路径',
    `inference_time` BIGINT DEFAULT NULL COMMENT '推理时间(ms)',
    `user_id` BIGINT DEFAULT NULL COMMENT '检测用户ID',
    `denoise_method` VARCHAR(20) DEFAULT 'none' COMMENT '去噪方法',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '逻辑删除',
    PRIMARY KEY (`id`),
    KEY `idx_image_id` (`image_id`),
    KEY `idx_model_name` (`model_name`),
    KEY `idx_result` (`result`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检测记录表';

-- 4. 检测报告表
DROP TABLE IF EXISTS `detection_report`;
CREATE TABLE `detection_report` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `detection_id` BIGINT NOT NULL COMMENT '检测记录ID',
    `title` VARCHAR(255) NOT NULL COMMENT '报告标题',
    `image_name` VARCHAR(255) DEFAULT NULL COMMENT '影像名称',
    `model_name` VARCHAR(50) DEFAULT NULL COMMENT '使用模型',
    `result` VARCHAR(20) DEFAULT NULL COMMENT '检测结果',
    `diagnosis` TEXT DEFAULT NULL COMMENT '诊断建议',
    `remark` TEXT DEFAULT NULL COMMENT '备注',
    `user_id` BIGINT DEFAULT NULL COMMENT '用户ID',
    `pdf_path` VARCHAR(500) DEFAULT NULL COMMENT 'PDF文件路径',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '逻辑删除',
    PRIMARY KEY (`id`),
    KEY `idx_detection_id` (`detection_id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检测报告表';

-- =============================================
-- 插入初始数据
-- =============================================

-- 管理员账号 (密码: admin123)
INSERT INTO `sys_user` (`username`, `password`, `email`, `phone`, `role`, `status`)
VALUES ('admin', 'admin123', 'admin@pinewilt.com', '13800138000', 'admin', 'active');

-- 普通用户 (密码: user123)
INSERT INTO `sys_user` (`username`, `password`, `email`, `phone`, `role`, `status`)
VALUES ('user', 'user123', 'user@pinewilt.com', '13900139000', 'user', 'active');
