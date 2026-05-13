<template>
  <div class="model-compare">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模型对比分析</span>
          <el-button type="primary" @click="handleStartCompare">
            <el-icon><VideoPlay /></el-icon>
            开始对比
          </el-button>
        </div>
      </template>

      <!-- 模型选择区域 -->
      <el-form :inline="true" :model="compareParams" class="compare-form">
        <el-form-item label="选择模型">
          <el-checkbox-group v-model="compareParams.models">
            <el-checkbox label="Improved U-Net" />
            <el-checkbox label="Standard U-Net" />
            <el-checkbox label="Mask R-CNN" />
            <el-checkbox label="YOLOv8" />
            <el-checkbox label="YOLOv10" />
            <el-checkbox label="YOLOv11" />
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="测试数据集">
          <el-select v-model="compareParams.dataset" placeholder="请选择数据集">
            <el-option label="测试集A" value="testA" />
            <el-option label="测试集B" value="testB" />
            <el-option label="全部测试集" value="all" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCompare">开始对比</el-button>
          <el-button @click="resetCompare">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 对比结果表格 -->
      <div v-if="compareResults.length > 0">
        <el-divider content-position="left">性能指标对比</el-divider>

        <el-table :data="compareResults" style="width: 100%" stripe>
          <el-table-column prop="modelName" label="模型名称" width="150" />
          <el-table-column prop="dice" label="Dice系数" width="120">
            <template #default="{ row }">
              <el-tag :type="getScoreType(row.dice)">{{ row.dice.toFixed(4) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="iou" label="IoU" width="120">
            <template #default="{ row }">
              <el-tag :type="getScoreType(row.iou)">{{ row.iou.toFixed(4) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="precision" label="精确率" width="120">
            <template #default="{ row }">
              {{ (row.precision * 100).toFixed(2) }}%
            </template>
          </el-table-column>
          <el-table-column prop="recall" label="召回率" width="120">
            <template #default="{ row }">
              {{ (row.recall * 100).toFixed(2) }}%
            </template>
          </el-table-column>
          <el-table-column prop="f1Score" label="F1分数" width="120">
            <template #default="{ row }">
              {{ (row.f1Score * 100).toFixed(2) }}%
            </template>
          </el-table-column>
          <el-table-column prop="accuracy" label="准确率" width="120">
            <template #default="{ row }">
              {{ (row.accuracy * 100).toFixed(2) }}%
            </template>
          </el-table-column>
          <el-table-column prop="inferenceTime" label="推理时间(ms)" width="130" />
          <el-table-column prop="params" label="参数量(M)" width="120">
            <template #default="{ row }">
              {{ (row.params / 1000000).toFixed(2) }}
            </template>
          </el-table-column>
        </el-table>

        <!-- 图表对比 -->
        <el-divider content-position="left">可视化对比</el-divider>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <div ref="barChartRef" style="width: 100%; height: 400px;" />
          </el-col>
          <el-col :span="12">
            <div ref="radarChartRef" style="width: 100%; height: 400px;" />
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="24">
            <div ref="lineChartRef" style="width: 100%; height: 400px;" />
          </el-col>
        </el-row>

        <!-- 详细分析 -->
        <el-divider content-position="left">详细分析</el-divider>

        <el-descriptions :column="1" border style="margin-top: 20px;">
          <el-descriptions-item label="最佳模型">
            {{ getBestModel().name }} (Dice: {{ getBestModel().dice.toFixed(4) }})
          </el-descriptions-item>
          <el-descriptions-item label="最快模型">
            {{ getFastestModel().name }} ({{ getFastestModel().inferenceTime }}ms)
          </el-descriptions-item>
          <el-descriptions-item label="最轻量模型">
            {{ getLightestModel().name }} ({{ (getLightestModel().params / 1000000).toFixed(2) }}M)
          </el-descriptions-item>
          <el-descriptions-item label="推荐模型">
            {{ getRecommendedModel().name }} - 综合考虑精度和速度
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-empty v-else description="请选择模型并开始对比" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { modelApi } from '../api'

const compareParams = reactive({
  models: ['Improved U-Net', 'Mask R-CNN', 'YOLOv8'],
  dataset: 'all'
})

const compareResults = ref([])
const barChartRef = ref(null)
const radarChartRef = ref(null)
const lineChartRef = ref(null)

let barChart = null
let radarChart = null
let lineChart = null

onMounted(() => {
  // 初始化图表
})

const handleCompare = async () => {
  if (compareParams.models.length < 2) {
    ElMessage.warning('请至少选择2个模型进行对比')
    return
  }

  try {
    const res = await modelApi.compare({
      models: compareParams.models,
      dataset: compareParams.dataset
    })
    compareResults.value = res.data
    await nextTick()
    initCharts()
  } catch (error) {
    ElMessage.error('模型对比失败')
  }
}

const handleStartCompare = () => {
  handleCompare()
}

const resetCompare = () => {
  compareParams.models = ['Improved U-Net', 'Mask R-CNN', 'YOLOv8']
  compareParams.dataset = 'all'
  compareResults.value = []
}

const initCharts = () => {
  initBarChart()
  initRadarChart()
  initLineChart()
}

const initBarChart = () => {
  if (!barChartRef.value) return
  barChart = echarts.init(barChartRef.value)

  const option = {
    title: {
      text: '模型性能对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['Dice系数', 'IoU'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: compareResults.value.map(m => m.modelName)
    },
    yAxis: {
      type: 'value',
      max: 1
    },
    series: [
      {
        name: 'Dice系数',
        type: 'bar',
        data: compareResults.value.map(m => m.dice)
      },
      {
        name: 'IoU',
        type: 'bar',
        data: compareResults.value.map(m => m.iou)
      }
    ]
  }

  barChart.setOption(option)
}

const initRadarChart = () => {
  if (!radarChartRef.value) return
  radarChart = echarts.init(radarChartRef.value)

  const indicator = [
    { name: 'Dice系数', max: 1 },
    { name: 'IoU', max: 1 },
    { name: '精确率', max: 1 },
    { name: '召回率', max: 1 },
    { name: 'F1分数', max: 1 }
  ]

  const series = compareResults.value.map(m => ({
    name: m.modelName,
    value: [m.dice, m.iou, m.precision, m.recall, m.f1Score]
  }))

  const option = {
    title: {
      text: '模型雷达图对比',
      left: 'center'
    },
    tooltip: {},
    legend: {
      data: compareResults.value.map(m => m.modelName),
      bottom: 0
    },
    radar: {
      indicator
    },
    series: [{
      type: 'radar',
      data: series
    }]
  }

  radarChart.setOption(option)
}

const initLineChart = () => {
  if (!lineChartRef.value) return
  lineChart = echarts.init(lineChartRef.value)

  const option = {
    title: {
      text: '推理时间对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: compareResults.value.map(m => m.modelName)
    },
    yAxis: {
      type: 'value',
      name: '时间(ms)'
    },
    series: [{
      type: 'line',
      data: compareResults.value.map(m => m.inferenceTime),
      smooth: true,
      itemStyle: {
        color: '#409eff'
      }
    }]
  }

  lineChart.setOption(option)
}

const getScoreType = (score) => {
  if (score >= 0.9) return 'success'
  if (score >= 0.8) return 'warning'
  return 'danger'
}

const getBestModel = () => {
  if (compareResults.value.length === 0) return { name: '-', dice: 0 }
  return compareResults.value.reduce((best, current) => {
    return current.dice > best.dice ? current : best
  })
}

const getFastestModel = () => {
  if (compareResults.value.length === 0) return { name: '-', inferenceTime: 0 }
  return compareResults.value.reduce((fastest, current) => {
    return current.inferenceTime < fastest.inferenceTime ? current : fastest
  })
}

const getLightestModel = () => {
  if (compareResults.value.length === 0) return { name: '-', params: 0 }
  return compareResults.value.reduce((lightest, current) => {
    return current.params < lightest.params ? current : lightest
  })
}

const getRecommendedModel = () => {
  // 综合考虑Dice系数和推理时间
  if (compareResults.value.length === 0) return { name: '-' }
  return compareResults.value.reduce((best, current) => {
    const bestScore = best.dice / (best.inferenceTime / 100)
    const currentScore = current.dice / (current.inferenceTime / 100)
    return currentScore > bestScore ? current : best
  })
}
</script>

<style scoped>
.model-compare {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.compare-form {
  margin-bottom: 20px;
}
</style>
