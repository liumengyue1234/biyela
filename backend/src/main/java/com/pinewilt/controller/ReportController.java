package com.pinewilt.controller;

import com.pinewilt.entity.DetectionReport;
import com.pinewilt.service.DetectionReportService;
import com.pinewilt.util.JwtUtil;
import com.pinewilt.util.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Map;

/**
 * 检测报告控制器
 */
@Slf4j
@RestController
@RequestMapping("/api/report")
public class ReportController {

    @Autowired
    private DetectionReportService reportService;

    @Autowired
    private JwtUtil jwtUtil;

    /**
     * 获取报告列表
     */
    @GetMapping("/list")
    public Result<?> list(HttpServletRequest request) {
        Long userId = jwtUtil.getUserIdFromRequest(request);
        List<DetectionReport> reports = reportService.list();
        return Result.success(reports);
    }

    /**
     * 获取报告详情
     */
    @GetMapping("/{id}")
    public Result<?> getDetail(@PathVariable Long id) {
        DetectionReport report = reportService.getById(id);
        if (report == null) {
            return Result.error("报告不存在");
        }
        return Result.success(report);
    }

    /**
     * 生成报告
     */
    @PostMapping("/generate")
    public Result<?> generate(@RequestBody Map<String, Object> params) {
        try {
            Long detectionId = Long.valueOf(params.get("detectionId").toString());
            String title = (String) params.get("title");
            String remark = (String) params.get("remark");

            DetectionReport report = reportService.generateReport(detectionId, title, remark);
            return Result.success(report);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 导出PDF报告
     */
    @GetMapping("/{id}/export")
    public Result<?> exportPDF(@PathVariable Long id) {
        try {
            byte[] pdfData = reportService.exportPDF(id);
            return Result.success(pdfData);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 删除报告
     */
    @DeleteMapping("/{id}")
    public Result<?> delete(@PathVariable Long id) {
        reportService.removeById(id);
        return Result.success("删除成功");
    }
}
