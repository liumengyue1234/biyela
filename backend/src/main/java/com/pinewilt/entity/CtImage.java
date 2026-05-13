package com.pinewilt.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * CT影像实体类
 */
@Data
@TableName("ct_image")
public class CtImage {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String imageName;

    private String filePath;

    private String fileSize;

    private String format;     // jpg/png/dcm

    private Integer width;

    private Integer height;

    private String status;     // pending/detected/processing

    private Long userId;

    private String denoiseMethod;  // none/bilateral/gaussian/median/nlmeans

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    @TableLogic
    private Integer deleted;
}
