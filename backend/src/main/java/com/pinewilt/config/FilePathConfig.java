package com.pinewilt.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

import javax.annotation.PostConstruct;
import java.io.File;

/**
 * 文件路径配置
 * 启动时自动创建上传目录
 */
@Configuration
public class FilePathConfig {

    @Value("${file.upload-path:./uploads/}")
    private String uploadPath;

    @Value("${file.image-path:./uploads/images/}")
    private String imagePath;

    @Value("${file.result-path:./uploads/results/}")
    private String resultPath;

    @Value("${file.report-path:./uploads/reports/}")
    private String reportPath;

    @PostConstruct
    public void init() {
        createDirIfNotExists(uploadPath);
        createDirIfNotExists(imagePath);
        createDirIfNotExists(resultPath);
        createDirIfNotExists(reportPath);
    }

    private void createDirIfNotExists(String path) {
        File dir = new File(path);
        if (!dir.exists()) {
            boolean created = dir.mkdirs();
            if (created) {
                System.out.println("创建目录: " + dir.getAbsolutePath());
            }
        }
    }
}
