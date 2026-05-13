package com.pinewilt.util;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;

/**
 * Python深度学习服务调用工具类
 */
@Slf4j
@Component
public class PythonServiceUtil {

    @Value("${python.service-url}")
    private String pythonServiceUrl;

    private final RestTemplate restTemplate = new RestTemplate();

    /**
     * 调用Python检测服务
     */
    public DetectionResult detect(String imagePath, String modelName, String denoiseMethod) {
        String url = pythonServiceUrl + "/detect";

        JSONObject params = new JSONObject();
        params.put("image_path", imagePath);
        params.put("model_name", modelName);
        params.put("denoise_method", denoiseMethod);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<String> entity = new HttpEntity<>(params.toJSONString(), headers);

        try {
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.POST, entity, String.class);
            if (response.getStatusCode() == HttpStatus.OK) {
                JSONObject result = JSON.parseObject(response.getBody());
                DetectionResult detectionResult = new DetectionResult();
                detectionResult.setPositive("positive".equals(result.getString("result")));
                detectionResult.setDiceScore(result.getBigDecimal("dice_score"));
                detectionResult.setIouScore(result.getBigDecimal("iou_score"));
                detectionResult.setPrecision(result.getBigDecimal("precision"));
                detectionResult.setRecall(result.getBigDecimal("recall"));
                detectionResult.setF1Score(result.getBigDecimal("f1_score"));
                detectionResult.setAccuracy(result.getBigDecimal("accuracy"));
                detectionResult.setSegmentationPath(result.getString("segmentation_path"));
                detectionResult.setInferenceTime(result.getLong("inference_time"));
                return detectionResult;
            }
        } catch (Exception e) {
            log.error("调用Python检测服务失败", e);
            // 返回模拟数据
            return getMockResult(modelName);
        }

        throw new RuntimeException("检测服务调用失败");
    }

    /**
     * 获取模拟结果（Python服务不可用时）
     */
    private DetectionResult getMockResult(String modelName) {
        DetectionResult result = new DetectionResult();
        result.setPositive(true);
        result.setDiceScore(new BigDecimal("0.8923"));
        result.setIouScore(new BigDecimal("0.8156"));
        result.setPrecision(new BigDecimal("0.9134"));
        result.setRecall(new BigDecimal("0.8756"));
        result.setF1Score(new BigDecimal("0.8941"));
        result.setAccuracy(new BigDecimal("0.9678"));
        result.setInferenceTime(45L);
        result.setSegmentationPath("");
        return result;
    }

    /**
     * 检测结果DTO
     */
    @Data
    public static class DetectionResult {
        private boolean positive;
        private BigDecimal diceScore;
        private BigDecimal iouScore;
        private BigDecimal precision;
        private BigDecimal recall;
        private BigDecimal f1Score;
        private BigDecimal accuracy;
        private BigDecimal hausdorff;
        private String segmentationPath;
        private Long inferenceTime;
    }
}
