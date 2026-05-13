package com.pinewilt.controller;

import com.pinewilt.util.Result;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * 模型对比控制器
 */
@RestController
@RequestMapping("/api/model")
public class ModelController {

    /**
     * 模型对比
     */
    @PostMapping("/compare")
    public Result<?> compare(@RequestBody Map<String, Object> params) {
        List<String> models = (List<String>) params.get("models");

        // 返回模拟对比结果
        // 实际项目中应调用Python服务获取真实数据
        List<Map<String, Object>> results = new ArrayList<>();

        if (models.contains("Improved U-Net")) {
            Map<String, Object> m = new HashMap<>();
            m.put("modelName", "Improved U-Net");
            m.put("dice", 0.8923);
            m.put("iou", 0.8156);
            m.put("precision", 0.9134);
            m.put("recall", 0.8756);
            m.put("f1Score", 0.8941);
            m.put("accuracy", 0.9678);
            m.put("inferenceTime", 45);
            m.put("params", 34567890L);
            results.add(m);
        }

        if (models.contains("Standard U-Net")) {
            Map<String, Object> m = new HashMap<>();
            m.put("modelName", "Standard U-Net");
            m.put("dice", 0.8234);
            m.put("iou", 0.7456);
            m.put("precision", 0.8567);
            m.put("recall", 0.7923);
            m.put("f1Score", 0.8231);
            m.put("accuracy", 0.9412);
            m.put("inferenceTime", 38);
            m.put("params", 31024567L);
            results.add(m);
        }

        if (models.contains("Mask R-CNN")) {
            Map<String, Object> m = new HashMap<>();
            m.put("modelName", "Mask R-CNN");
            m.put("dice", 0.8567);
            m.put("iou", 0.7823);
            m.put("precision", 0.8912);
            m.put("recall", 0.8234);
            m.put("f1Score", 0.8559);
            m.put("accuracy", 0.9534);
            m.put("inferenceTime", 120);
            m.put("params", 44567890L);
            results.add(m);
        }

        if (models.contains("YOLOv8")) {
            Map<String, Object> m = new HashMap<>();
            m.put("modelName", "YOLOv8");
            m.put("dice", 0.8123);
            m.put("iou", 0.7234);
            m.put("precision", 0.8456);
            m.put("recall", 0.7812);
            m.put("f1Score", 0.8121);
            m.put("accuracy", 0.9323);
            m.put("inferenceTime", 15);
            m.put("params", 11234567L);
            results.add(m);
        }

        if (models.contains("YOLOv10")) {
            Map<String, Object> m = new HashMap<>();
            m.put("modelName", "YOLOv10");
            m.put("dice", 0.8345);
            m.put("iou", 0.7567);
            m.put("precision", 0.8678);
            m.put("recall", 0.8023);
            m.put("f1Score", 0.8341);
            m.put("accuracy", 0.9401);
            m.put("inferenceTime", 12);
            m.put("params", 10234567L);
            results.add(m);
        }

        if (models.contains("YOLOv11")) {
            Map<String, Object> m = new HashMap<>();
            m.put("modelName", "YOLOv11");
            m.put("dice", 0.8456);
            m.put("iou", 0.7678);
            m.put("precision", 0.8789);
            m.put("recall", 0.8145);
            m.put("f1Score", 0.8455);
            m.put("accuracy", 0.9456);
            m.put("inferenceTime", 10);
            m.put("params", 9876543L);
            results.add(m);
        }

        return Result.success(results);
    }

    /**
     * 获取可用模型列表
     */
    @GetMapping("/list")
    public Result<?> getModelList() {
        List<Map<String, Object>> models = new ArrayList<>();

        String[][] modelData = {
            {"Improved U-Net", "改进U-Net (CBAM+残差+多尺度)", "segmentation"},
            {"Standard U-Net", "标准U-Net (对比基线)", "segmentation"},
            {"Mask R-CNN", "Mask R-CNN实例分割", "instance_segmentation"},
            {"YOLOv8", "YOLOv8目标检测", "detection"},
            {"YOLOv10", "YOLOv10目标检测", "detection"},
            {"YOLOv11", "YOLOv11目标检测", "detection"},
        };

        for (String[] data : modelData) {
            Map<String, Object> m = new HashMap<>();
            m.put("name", data[0]);
            m.put("description", data[1]);
            m.put("type", data[2]);
            models.add(m);
        }

        return Result.success(models);
    }
}
