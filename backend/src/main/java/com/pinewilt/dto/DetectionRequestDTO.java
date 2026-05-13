package com.pinewilt.dto;

import lombok.Data;

/**
 * 检测请求DTO
 */
@Data
public class DetectionRequestDTO {

    private Long imageId;

    private String modelName;

    private String denoiseMethod;

    private Boolean saveResult;
}
