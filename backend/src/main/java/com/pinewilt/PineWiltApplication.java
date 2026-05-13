package com.pinewilt;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * CT图像松材线虫病检测系统 - 启动类
 */
@SpringBootApplication
@MapperScan("com.pinewilt.mapper")
public class PineWiltApplication {

    public static void main(String[] args) {
        SpringApplication.run(PineWiltApplication.class, args);
        System.out.println("========================================");
        System.out.println("  CT图像松材线虫病检测系统启动成功！");
        System.out.println("  访问地址: http://localhost:8080");
        System.out.println("========================================");
    }
}
