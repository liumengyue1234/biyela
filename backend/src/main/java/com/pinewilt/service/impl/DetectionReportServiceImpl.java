package com.pinewilt.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.pinewilt.entity.DetectionReport;
import com.pinewilt.mapper.DetectionReportMapper;
import com.pinewilt.service.DetectionReportService;
import com.pinewilt.entity.DetectionRecord;
import com.pinewilt.mapper.DetectionRecordMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;

/**
 * 检测报告Service实现类
 */
@Slf4j
@Service
public class DetectionReportServiceImpl extends ServiceImpl<DetectionReportMapper, DetectionReport>
        implements DetectionReportService {

    @Autowired
    private DetectionRecordMapper detectionRecordMapper;

    @Value("${file.report-path}")
    private String reportPath;

    @Override
    public DetectionReport generateReport(Long detectionId, String title, String remark) {
        DetectionRecord record = detectionRecordMapper.selectById(detectionId);
        if (record == null) {
            throw new RuntimeException("检测记录不存在");
        }

        DetectionReport report = new DetectionReport();
        report.setDetectionId(detectionId);
        report.setTitle(title != null ? title : record.getImageName() + " - 检测报告");
        report.setImageName(record.getImageName());
        report.setModelName(record.getModelName());
        report.setResult(record.getResult());
        report.setRemark(remark);
        report.setUserId(record.getUserId());

        // 生成诊断建议
        String diagnosis = generateDiagnosis(record);
        report.setDiagnosis(diagnosis);

        save(report);
        return report;
    }

    @Override
    public byte[] exportPDF(Long reportId) {
        DetectionReport report = getById(reportId);
        if (report == null) {
            throw new RuntimeException("报告不存在");
        }
        // 实际项目中使用iText等库生成PDF
        // 此处返回简化实现
        throw new RuntimeException("PDF导出功能需要iText库支持");
    }

    /**
     * 生成诊断建议
     */
    private String generateDiagnosis(DetectionRecord record) {
        StringBuilder sb = new StringBuilder();
        sb.append("检测模型: ").append(record.getModelName()).append("\n");
        sb.append("检测结果: ").append("positive".equals(record.getResult()) ? "阳性（检测到松材线虫病特征）" : "阴性（未检测到松材线虫病特征）").append("\n");

        if (record.getDiceScore() != null) {
            sb.append("Dice系数: ").append(record.getDiceScore()).append("\n");
        }
        if (record.getIouScore() != null) {
            sb.append("IoU: ").append(record.getIouScore()).append("\n");
        }

        if ("positive".equals(record.getResult())) {
            sb.append("\n诊断建议：\n");
            sb.append("1. CT影像中检测到松材线虫病典型特征，建议进一步取样检测确认。\n");
            sb.append("2. 建议对周边松林进行排查，防止病害扩散。\n");
            sb.append("3. 可结合其他检测方法（如PCR检测）进行综合判断。\n");
        } else {
            sb.append("\n诊断建议：\n");
            sb.append("1. CT影像中未检测到松材线虫病特征，建议定期复查。\n");
            sb.append("2. 继续保持对松林的健康监测。\n");
        }

        return sb.toString();
    }
}
