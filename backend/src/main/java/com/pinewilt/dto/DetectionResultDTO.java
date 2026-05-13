package com.pinewilt.dto;

import lombok.Data;
import java.math.BigDecimal;

/**
 * 检测结果DTO
 */
@Data
public class DetectionResultDTO {

    private Long id;

    private Long imageId;

    private String imageName;

    private String modelName;

    private String result;

    private BigDecimal diceScore;

    private BigDecimal iouScore;

    private BigDecimal precision;

    private BigDecimal recall;

    private BigDecimal f1Score;

    private BigDecimal accuracy;

    private BigDecimal hausdorff;

    private String segmentationPath;

    private String originalImagePath;

    private Long inferenceTime;

    private String denoiseMethod;

    private String createTime;
}
