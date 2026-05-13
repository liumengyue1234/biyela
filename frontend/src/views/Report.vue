<template>
  <div class="report">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>检测报告</span>
          <div>
            <el-button type="primary" @click="handleGenerate">
              <el-icon><Plus /></el-icon>
              生成报告
            </el-button>
            <el-button type="success" @click="handleExport" :disabled="!currentReport">
              <el-icon><Download /></el-icon>
              导出PDF
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧报告列表 -->
        <el-col :span="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索报告..."
            clearable
            style="margin-bottom: 15px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-table
            :data="filteredReportList"
            style="width: 100%"
            highlight-current-row
            @row-click="handleSelectReport"
          >
            <el-table-column prop="title" label="报告标题" />
            <el-table-column prop="createTime" label="生成时间" width="120" />
          </el-table>
        </el-col>

        <!-- 右侧报告详情 -->
        <el-col :span="16" v-if="currentReport">
          <div class="report-detail">
            <h2>{{ currentReport.title }}</h2>
            <el-descriptions :column="2" border style="margin-top: 20px;">
              <el-descriptions-item label="影像名称">{{ currentReport.imageName }}</el-descriptions-item>
              <el-descriptions-item label="检测模型">{{ currentReport.modelName }}</el-descriptions-item>
              <el-descriptions-item label="检测结果">
                <el-tag :type="currentReport.result === 'positive' ? 'danger' : 'success'">
                  {{ currentReport.result === 'positive' ? '阳性' : '阴性' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="生成时间">{{ currentReport.createTime }}</el-descriptions-item>
            </el-descriptions>

            <el-divider />

            <h3>检测指标</h3>
            <el-row :gutter="20" style="margin-top: 15px;">
              <el-col :span="8" v-for="metric in metricsList" :key="metric.name">
                <el-card shadow="hover" class="metric-card">
                  <div class="metric-value">{{ metric.value }}</div>
                  <div class="metric-name">{{ metric.name }}</div>
                </el-card>
              </el-col>
            </el-row>

            <el-divider />

            <h3>影像对比</h3>
            <el-row :gutter="20" style="margin-top: 15px;">
              <el-col :span="12">
                <h4>原始CT影像</h4>
                <img :src="currentReport.originalImage" alt="原始影像" style="width: 100%;" />
              </el-col>
              <el-col :span="12">
                <h4>分割结果</h4>
                <img :src="currentReport.segmentationImage" alt="分割结果" style="width: 100%;" />
              </el-col>
            </el-row>

            <el-divider />

            <h3>诊断建议</h3>
            <div class="diagnosis" style="margin-top: 15px;">
              <el-alert
                :type="currentReport.result === 'positive' ? 'error' : 'success'"
                :title="currentReport.result === 'positive' ? '检测到松材线虫病特征' : '未检测到松材线虫病特征'"
                show-icon
                :closable="false"
              />
              <div class="diagnosis-content" style="margin-top: 15px;">
                {{ currentReport.diagnosis }}
              </div>
            </div>
          </div>
        </el-col>

        <el-col :span="16" v-else>
          <el-empty description="请选择一份报告查看详情" />
        </el-col>
      </el-row>
    </el-card>

    <!-- 生成报告对话框 -->
    <el-dialog v-model="generateDialogVisible" title="生成检测报告" width="600px">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="选择检测记录">
          <el-select v-model="generateForm.detectionId" placeholder="请选择检测记录">
            <el-option
              v-for="item in detectionList"
              :key="item.id"
              :label="item.imageName"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="报告标题">
          <el-input v-model="generateForm.title" placeholder="请输入报告标题" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="generateForm.remark"
            type="textarea"
            :rows="4"
            placeholder="请输入备注信息（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGenerate">确定生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { reportApi } from '../api'

const loading = ref(false)
const reportList = ref([])
const filteredReportList = computed(() => {
  if (!searchKeyword.value) return reportList.value
  return reportList.value.filter(r => r.title.includes(searchKeyword.value))
})
const searchKeyword = ref('')
const currentReport = ref(null)
const generateDialogVisible = ref(false)
const detectionList = ref([])

const generateForm = reactive({
  detectionId: '',
  title: '',
  remark: ''
})

const metricsList = computed(() => {
  if (!currentReport.value) return []
  return [
    { name: 'Dice系数', value: currentReport.value.diceScore },
    { name: 'IoU', value: currentReport.value.iouScore },
    { name: '精确率', value: currentReport.value.precision },
    { name: '召回率', value: currentReport.value.recall },
    { name: 'F1分数', value: currentReport.value.f1Score },
    { name: '准确率', value: currentReport.value.accuracy }
  ]
})

onMounted(() => {
  getReportList()
})

const getReportList = async () => {
  loading.value = true
  try {
    const res = await reportApi.list()
    reportList.value = res.data
  } catch (error) {
    ElMessage.error('获取报告列表失败')
  } finally {
    loading.value = false
  }
}

const handleSelectReport = async (row) => {
  try {
    const res = await reportApi.getDetail(row.id)
    currentReport.value = res.data
  } catch (error) {
    ElMessage.error('获取报告详情失败')
  }
}

const handleGenerate = async () => {
  try {
    const res = await reportApi.getDetectionList()
    detectionList.value = res.data
    generateDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取检测记录失败')
  }
}

const submitGenerate = async () => {
  try {
    await reportApi.generate(generateForm)
    ElMessage.success('报告生成成功')
    generateDialogVisible.value = false
    getReportList()
  } catch (error) {
    ElMessage.error('报告生成失败')
  }
}

const handleExport = async () => {
  if (!currentReport.value) return
  try {
    const res = await reportApi.exportPDF(currentReport.value.id)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${currentReport.value.title}.pdf`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}
</script>

<style scoped>
.report {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-detail {
  padding: 0 20px;
}

.metric-card {
  text-align: center;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.metric-name {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.diagnosis-content {
  line-height: 1.8;
  color: #606266;
}
</style>
