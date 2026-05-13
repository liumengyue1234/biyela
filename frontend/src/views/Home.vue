<template>
  <div class="home-container">
    <el-row :gutter="20" class="status-row">
      <el-col :span="6" v-for="item in statusCards" :key="item.title">
        <el-card shadow="hover" class="status-card">
          <div class="card-content">
            <div class="card-icon" :style="{ background: item.bg }">
              <el-icon :size="32"><component :is="item.icon" /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ item.value }}</div>
              <div class="card-title">{{ item.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>系统概览</span>
            </div>
          </template>
          <div ref="overviewChart" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>检测类别分布</span>
            </div>
          </template>
          <div ref="pieChart" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row class="quick-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="goDetection">
              <el-icon><Upload /></el-icon>
              上传CT影像检测
            </el-button>
            <el-button type="success" size="large" @click="goHistory">
              <el-icon><Clock /></el-icon>
              查看历史记录
            </el-button>
            <el-button type="warning" size="large" @click="goReport">
              <el-icon><Document /></el-icon>
              生成检测报告
            </el-button>
            <el-button type="info" size="large" @click="goModelCompare">
              <el-icon><DataAnalysis /></el-icon>
              模型对比分析
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { PictureFilled, DataAnalysis, Document, User } from '@element-plus/icons-vue'

const router = useRouter()
const overviewChart = ref(null)
const pieChart = ref(null)

const statusCards = ref([
  { title: 'CT影像总数', value: '1,326', icon: PictureFilled, bg: '#409eff20' },
  { title: '检测次数', value: '856', icon: DataAnalysis, bg: '#67c23a20' },
  { title: '生成报告', value: '432', icon: Document, bg: '#e6a23c20' },
  { title: '用户数量', value: '12', icon: User, bg: '#90939920' },
])

const goDetection = () => router.push('/detection')
const goHistory = () => router.push('/history')
const goReport = () => router.push('/report')
const goModelCompare = () => router.push('/model-compare')

onMounted(() => {
  // 折线图
  const chart1 = echarts.init(overviewChart.value)
  chart1.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['检测数量', '病变检出数'] },
    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月'] },
    yAxis: { type: 'value' },
    series: [
      { name: '检测数量', type: 'line', data: [120, 200, 150, 80, 70], smooth: true },
      { name: '病变检出数', type: 'line', data: [80, 140, 100, 50, 45], smooth: true },
    ]
  })

  // 饼图
  const chart2 = echarts.init(pieChart.value)
  chart2.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 856, name: '已检测' },
        { value: 470, name: '检出病变' },
      ],
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
    }]
  })

  window.addEventListener('resize', () => {
    chart1.resize()
    chart2.resize()
  })
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}
.status-row {
  margin-bottom: 20px;
}
.status-card {
  cursor: pointer;
  transition: transform 0.2s;
}
.status-card:hover {
  transform: translateY(-4px);
}
.card-content {
  display: flex;
  align-items: center;
  gap: 16px;
}
.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
}
.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}
.card-title {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
.chart-row {
  margin-bottom: 20px;
}
.chart-box {
  height: 300px;
}
.card-header {
  font-weight: 600;
  font-size: 16px;
}
.quick-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
</style>
