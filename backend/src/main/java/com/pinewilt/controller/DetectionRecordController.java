package com.pinewilt.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.pinewilt.entity.DetectionRecord;
import com.pinewilt.service.DetectionRecordService;
import com.pinewilt.util.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 检测记录控制器
 */
@RestController
@RequestMapping("/api/detection")
public class DetectionRecordController {

    @Autowired
    private DetectionRecordService detectionRecordService;

    /**
     * 获取历史检测记录
     */
    @GetMapping("/history")
    public Result<?> getHistory(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String imageName,
            @RequestParam(required = false) String result) {

        LambdaQueryWrapper<DetectionRecord> wrapper = new LambdaQueryWrapper<>();
        if (imageName != null && !imageName.isEmpty()) {
            wrapper.like(DetectionRecord::getImageName, imageName);
        }
        if (result != null && !result.isEmpty()) {
            wrapper.eq(DetectionRecord::getResult, result);
        }
        wrapper.orderByDesc(DetectionRecord::getCreateTime);

        Page<DetectionRecord> page = detectionRecordService.page(new Page<>(pageNum, pageSize), wrapper);
        return Result.success(page);
    }

    /**
     * 获取检测详情
     */
    @GetMapping("/{id}")
    public Result<?> getDetail(@PathVariable Long id) {
        DetectionRecord record = detectionRecordService.getDetail(id);
        if (record == null) {
            return Result.error("记录不存在");
        }
        return Result.success(record);
    }

    /**
     * 批量删除记录
     */
    @DeleteMapping("/batch")
    public Result<?> batchDelete(@RequestBody List<Long> ids) {
        detectionRecordService.removeByIds(ids);
        return Result.success("批量删除成功");
    }

    /**
     * 删除单条记录
     */
    @DeleteMapping("/{id}")
    public Result<?> delete(@PathVariable Long id) {
        detectionRecordService.removeById(id);
        return Result.success("删除成功");
    }
}
