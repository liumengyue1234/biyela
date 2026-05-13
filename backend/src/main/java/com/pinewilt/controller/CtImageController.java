package com.pinewilt.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.pinewilt.entity.CtImage;
import com.pinewilt.service.CtImageService;
import com.pinewilt.util.JwtUtil;
import com.pinewilt.util.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.servlet.http.HttpServletRequest;
import java.io.File;

/**
 * CT影像控制器
 */
@Slf4j
@RestController
@RequestMapping("/api/images")
public class CtImageController {

    @Autowired
    private CtImageService ctImageService;

    @Autowired
    private JwtUtil jwtUtil;

    /**
     * 上传CT影像
     */
    @PostMapping("/upload")
    public Result<?> upload(@RequestParam("file") MultipartFile file, HttpServletRequest request) {
        Long userId = jwtUtil.getUserIdFromRequest(request);
        CtImage ctImage = ctImageService.uploadImage(file, userId);
        return Result.success(ctImage);
    }

    /**
     * 获取影像列表
     */
    @GetMapping("/list")
    public Result<?> list(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String name,
            @RequestParam(required = false) String status) {

        LambdaQueryWrapper<CtImage> wrapper = new LambdaQueryWrapper<>();
        if (name != null && !name.isEmpty()) {
            wrapper.like(CtImage::getImageName, name);
        }
        if (status != null && !status.isEmpty()) {
            wrapper.eq(CtImage::getStatus, status);
        }
        wrapper.orderByDesc(CtImage::getCreateTime);

        Page<CtImage> page = ctImageService.page(new Page<>(pageNum, pageSize), wrapper);
        return Result.success(page);
    }

    /**
     * 提交检测
     */
    @PostMapping("/{id}/detect")
    public Result<?> detect(
            @PathVariable Long id,
            @RequestParam(defaultValue = "Improved U-Net") String modelName,
            @RequestParam(defaultValue = "none") String denoiseMethod) {
        try {
            Object result = ctImageService.detect(id, modelName, denoiseMethod);
            return Result.success(result);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 查看影像
     */
    @GetMapping("/view/{id}")
    public ResponseEntity<Resource> view(@PathVariable Long id) {
        CtImage ctImage = ctImageService.getById(id);
        if (ctImage == null) {
            return ResponseEntity.notFound().build();
        }

        File file = new File(ctImage.getFilePath());
        if (!file.exists()) {
            return ResponseEntity.notFound().build();
        }

        FileSystemResource resource = new FileSystemResource(file);
        String contentType = getContentType(ctImage.getFormat());

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + ctImage.getImageName() + "\"")
                .body(resource);
    }

    /**
     * 删除影像
     */
    @DeleteMapping("/{id}")
    public Result<?> delete(@PathVariable Long id) {
        ctImageService.removeById(id);
        return Result.success("删除成功");
    }

    private String getContentType(String format) {
        switch (format.toLowerCase()) {
            case "jpg":
            case "jpeg":
                return "image/jpeg";
            case "png":
                return "image/png";
            case "dcm":
                return "application/dicom";
            default:
                return "application/octet-stream";
        }
    }
}
