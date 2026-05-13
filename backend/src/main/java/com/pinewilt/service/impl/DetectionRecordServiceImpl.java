package com.pinewilt.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.pinewilt.entity.DetectionRecord;
import com.pinewilt.mapper.DetectionRecordMapper;
import com.pinewilt.service.DetectionRecordService;
import org.springframework.stereotype.Service;

/**
 * 检测记录Service实现类
 */
@Service
public class DetectionRecordServiceImpl extends ServiceImpl<DetectionRecordMapper, DetectionRecord>
        implements DetectionRecordService {

    @Override
    public DetectionRecord createRecord(DetectionRecord record) {
        save(record);
        return record;
    }

    @Override
    public DetectionRecord getDetail(Long id) {
        return getById(id);
    }
}
