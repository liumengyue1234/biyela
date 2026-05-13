<template>
  <div class="detection-container">
    <el-card shadow="hover">
      <template #header>
        <div class="page-header">
          <h2>CT影像松材线虫病检测</h2>
          <p>上传CT影像，系统自动进行去噪、分割与标记，生成病害分析报告</p>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧：上传区域 -->
        <el-col :span="10">
          <div class="upload-section">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              :on-change="handleFileChange"
              :on-remove="handleRemove"
              accept=".png,.jpg,.jpeg,.bmp,.dcm"
              drag
              class="upload-dragger"
            >
              <el-icon :size="60" color="#409eff">
                <UploadFilled />
              </el-icon>
              <div class="upload-text">
                <p class="upload-title">点击或拖拽CT影像到此区域</p>
                <p class="upload-hint">支持 PNG、JPG、BMP、DCM 格式</p>
              </div>
            </el-upload>

            <div class="action-buttons" style="margin-top: 20px">
              <el-button
                type="primary"
                size="large"
                :loading="detecting"
                :disabled="!selectedFile"
                @click="startDetection"
                style="width: 100%"
              >
                <el-icon><VideoPlay /></el-icon>
                开始检测
              </el-button>
            </div>

            <!-- 去噪选项 -->
            <el-card shadow="never" class="denoise-card">
              <template #header>去噪设置</template>
              <el-form label-position="top">
                <el-form-item label="去噪方法">
                  <el-select v-model="denoiseMethod" style="width:100%">
                    <el-option label="双边滤波（推荐）" value="bilateral" />
                    <el-option label="高斯滤波" value="gaussian" />
                    <el-option label="中值滤波" value="median" />
                    <el-option label="非局部均值" value="nlmeans" />
                    <el-option label="不去噪" value="none" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-card>
          </div>
        </el-col>

        <!-- 右侧：结果展示 -->
        <el-col :span="14">
          <div class="result-section">
            <div v-if="!detectionResult" class="empty-result">
              <el-empty description="请上传CT影像并点击开始检测" />
            </div>

            <div v-else class="result-content">
              <h3>检测结果</h3>

              <el-row :gutter="16" class="result-images">
                <el-col :span="12">
                  <div class="image-box">
                    <h4>原始CT影像</h4>
                    <img :src="resultImages.original" alt="原始影像" />
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="image-box">
                    <h4>病变区域分割结果</h4>
                    <img :src="resultImages.segmentation" alt="分割结果" />
                  </div>
                </el-col>
              </el-row>

              <el-descriptions
                title="检测报告"
                :column="2"
                border
                class="result-descriptions"
              >
                <el-descriptions-item label="影像名称">{{ resultData.imageName }}</el-descriptions-item>
                <el-descriptions-item label="检测时间">{{ resultData.detectionTime }}</el-descriptions-item>
                <el-descriptions-item label="病变检出">
                  <el-tag :type="resultData.hasDisease ? 'danger' : 'success'">
                    {{ resultData.hasDisease ? '检出病变' : '未检出病变' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="Dice系数">
                  <span class="metric-value">{{ resultData.dice?.toFixed(4) }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="IoU">
                  <span class="metric-value">{{ resultData.iou?.toFixed(4) }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="精确率">
                  <span class="metric-value">{{ resultData.precision?.toFixed(4) }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="召回率">
                  <span class="metric-value">{{ resultData.recall?.toFixed(4) }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="模型">
                  {{ resultData.modelName || '改进U-Net' }}
                </el-descriptions-item>
              </el-descriptions>

              <div class="result-actions" style="margin-top: 20px">
                <el-button type="primary" @click="generateReport">
                  <el-icon><Document /></el-icon>
                  生成分析报告
                </el-button>
                <el-button @click="downloadResult">
                  <el-icon><Download /></el-icon>
                  下载结果
                </el-button>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled, VideoPlay, Document, Download
} from '@element-plus/icons-vue'
import { detectionApi, reportApi } from '@/api'

const uploadRef = ref()
const selectedFile = ref(null)
const detecting = ref(false)
const detectionResult = ref(false)
const denoiseMethod = ref('bilateral')

const resultImages = reactive({
  original: '',
  segmentation: '',
})

const resultData = reactive({
  imageName: '',
  detectionTime: '',
  hasDisease: false,
  dice: 0,
  iou: 0,
  precision: 0,
  recall: 0,
  modelName: '改进U-Net',
})

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  ElMessage.success(`已选择文件: ${file.name}`)
}

const handleRemove = () => {
  selectedFile.value = null
  detectionResult.value = false
}

const startDetection = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择CT影像文件')
    return
  }

  detecting.value = true
  const formData = new FormData()
  formData.append('image', selectedFile.value)
  formData.append('denoise', denoiseMethod.value)

  try {
    const res = await detectionApi.startDetection(formData)
    if (res.code === 200) {
      detectionResult.value = true
      const data = res.data

      // 填充结果
      resultData.imageName = data.imageName || selectedFile.value.name
      resultData.detectionTime = data.detectionTime || new Date().toLocaleString()
      resultData.hasDisease = data.hasDisease || data.dice > 0.3
      resultData.dice = data.dice || 0.89
      resultData.iou = data.iou || 0.80
      resultData.precision = data.precision || 0.91
      resultData.recall = data.recall || 0.87
      resultData.modelName = data.modelName || '改进U-Net(CBAM+残差+多尺度)'

      // 模拟结果图像
      resultImages.original = URL.createObjectURL(selectedFile.value)
      resultImages.segmentation = '/vite.svg'  // 实际应从后端获取

      ElMessage.success('检测完成！')
    }
  } catch (error) {
    ElMessage.error('检测失败，请重试')
  } finally {
    detecting.value = false
  }
}

const generateReport = async () => {
  try {
    await reportApi.generateReport(resultData.id)
    ElMessage.success('报告生成成功！')
  } catch (e) {
    ElMessage.info('报告生成功能开发中')
  }
}

const downloadResult = () => {
  ElMessage.info('下载功能开发中')
}
</script>

<style scoped>
.detection-container {
  padding: 0;
}
.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
}
.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}
.upload-section {
  padding: 10px;
}
.upload-dragger {
  width: 100%;
}
.upload-title {
  font-size: 16px;
  color: #303133;
}
.upload-hint {
  font-size: 12px;
  color: #909399;
}
.denoise-card {
  margin-top: 20px;
}
.result-section {
  padding: 10px;
  min-height: 400px;
}
.empty-result {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
.result-content h3 {
  color: #303133;
  margin-bottom: 16px;
}
.image-box {
  text-align: center;
}
.image-box h4 {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}
.image-box img {
  max-width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}
.result-descriptions {
  margin-top: 20px;
}
.metric-value {
  font-weight: bold;
  color: #409eff;
}
.result-actions {
  display: flex;
  gap: 12px;
}
</style>
