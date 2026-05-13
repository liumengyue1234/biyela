package com.pinewilt.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 检测记录实体类
 */
@Data
@TableName("detection_record")
public class DetectionRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long imageId;

    private String imageName;

    private String modelName;       // Improved U-Net / Mask R-CNN / YOLO

    private String result;          // positive / negative

    private BigDecimal diceScore;

    private BigDecimal iouScore;

    private BigDecimal precision;

    private BigDecimal recall;

    private BigDecimal f1Score;

    private BigDecimal accuracy;

    private BigDecimal hausdorff;

    private String segmentationPath;

    private String originalImagePath;

    private Long inferenceTime;      // 推理时间(ms)

    private Long userId;

    private String denoiseMethod;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    @TableLogic
    private Integer deleted;
}
