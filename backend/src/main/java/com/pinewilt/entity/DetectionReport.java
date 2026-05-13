package com.pinewilt.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 检测报告实体类
 */
@Data
@TableName("detection_report")
public class DetectionReport {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long detectionId;

    private String title;

    private String imageName;

    private String modelName;

    private String result;

    private String diagnosis;

    private String remark;

    private Long userId;

    private String pdfPath;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    @TableLogic
    private Integer deleted;
}
