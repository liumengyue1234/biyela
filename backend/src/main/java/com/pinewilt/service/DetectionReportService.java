package com.pinewilt.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.pinewilt.entity.DetectionReport;

/**
 * 检测报告Service接口
 */
public interface DetectionReportService extends IService<DetectionReport> {

    /**
     * 生成检测报告
     */
    DetectionReport generateReport(Long detectionId, String title, String remark);

    /**
     * 导出PDF报告
     */
    byte[] exportPDF(Long reportId);
}
