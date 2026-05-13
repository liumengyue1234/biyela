package com.pinewilt.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.pinewilt.entity.DetectionRecord;

/**
 * 检测记录Service接口
 */
public interface DetectionRecordService extends IService<DetectionRecord> {

    /**
     * 创建检测记录
     */
    DetectionRecord createRecord(DetectionRecord record);

    /**
     * 获取检测详情
     */
    DetectionRecord getDetail(Long id);
}
