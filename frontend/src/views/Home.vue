<template>
  <div class="home">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="item in stats" :key="item.title">
        <el-card shadow="hover" class="stats-card">
          <div class="stats-content">
            <div class="stats-icon" :style="{background: item.bg}">
              <el-icon :size="28" color="#fff">
                <component :is="item.icon" />
              </el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ item.value }}</div>
              <div class="stats-title">{{ item.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>模型性能对比</template>
          <div ref="barChartRef" style="height:350px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>检测状态分布</template>
          <div ref="pieChartRef" style="height:350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近检测记录 -->
    <el-card shadow="hover" class="recent-card">
      <template #header>最近检测记录</template>
      <el-table :data="recentRecords" stripe style="width:100%">
        <el-table-column prop="imageName" label="影像名称" />
        <el-table-column prop="modelName" label="模型名称" />
        <el-table-column label="检测结果">
          <template #default="{ row }">
            <el-tag :type="row.result === 'positive' ? 'danger' : 'success'">
              {{ row.result === 'positive' ? '阳性' : '阴性' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="diceScore" label="Dice系数" />
        <el-table-column prop="createTime" label="检测时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  PictureFilled, Memo, User, DataAnalysis
} from '@element-plus/icons-vue'
import { detectionApi } from '@/api'

const stats = ref([
  { title: '影像总数', value: 0, icon: 'PictureFilled', bg: '#409eff' },
  { title: '检测次数', value: 0, icon: 'DataAnalysis', bg: '#67c23a' },
  { title: '用户数', value: 0, icon: 'User', bg: '#e6a23c' },
  { title: '报告数', value: 0, icon: 'Memo', bg: '#f56c6c' },
])

const recentRecords = ref([])
const barChartRef = ref(null)
const pieChartRef = ref(null)
let barChart = null
let pieChart = null

const fetchStats = async () => {
  try {
    const res = await detectionApi.getDetectionHistory({ page:1, pageSize:1 })
    if (res.code === 200) {
      stats.value[1].value = res.data.total || 0
    }
  } catch(e) {}
}

const fetchRecentRecords = async () => {
  try {
    const res = await detectionApi.getDetectionHistory({ page:1, pageSize:5 })
    if (res.code === 200) {
      recentRecords.value = res.data.records || res.data.list || []
    }
  } catch(e) {}
}

const initCharts = () => {
  nextTick(() => {
    if (barChartRef.value) {
      barChart = echarts.init(barChartRef.value)
      barChart.setOption({
        tooltip: { trigger:'axis' },
        legend: { bottom:0 },
        grid: { left:'3%', right:'4%', bottom:'15%', containLabel:true },
        xAxis: { type:'category', data:['U-Net','Mask R-CNN','YOLOv8','YOLOv10','YOLOv11'] },
        yAxis: { type:'value', max:1 },
        series: [
          { name:'Dice', type:'bar', data:[0.92,0.89,0.85,0.87,0.88], itemStyle:{ color:'#409eff' }},
          { name:'IoU', type:'bar', data:[0.84,0.81,0.76,0.79,0.80], itemStyle:{ color:'#67c23a' }},
        ]
      })
    }
    if (pieChartRef.value) {
      pieChart = echarts.init(pieChartRef.value)
      pieChart.setOption({
        tooltip: { trigger:'item' },
        legend: { bottom:0 },
        series:[{
          type:'pie',
          radius:['40%','70%'],
          avoidLabelOverlap:false,
          itemStyle:{ borderRadius:10, borderColor:'#fff', borderWidth:2 },
          label:{ show:false, position:'center' },
          emphasis:{ label:{ show:true, fontSize:'18', fontWeight:'bold' } },
          data:[
            { value:65, name:'检测完成', itemStyle:{ color:'#67c23a' }},
            { value:20, name:'等待中', itemStyle:{ color:'#409eff' }},
            { value:10, name:'检测中', itemStyle:{ color:'#e6a23c' }},
            { value:5, name:'失败', itemStyle:{ color:'#f56c6c' }},
          ]
        }]
      })
    }
  })
}

const handleResize = () => {
  barChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  fetchStats()
  fetchRecentRecords()
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  barChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.home {
  padding:0;
}
.stats-row {
  margin-bottom:20px;
}
.stats-card {
  cursor: pointer;
  transition: transform 0.3s;
}
.stats-card:hover {
  transform: translateY(-4px);
}
.stats-content {
  display: flex;
  align-items: center;
  gap:16px;
}
.stats-icon {
  width:52px;
  height:52px;
  border-radius:12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stats-info {
  flex:1;
}
.stats-value {
  font-size:24px;
  font-weight:bold;
  color: #303133;
}
.stats-title {
  font-size:13px;
  color: #909399;
  margin-top:4px;
}
.chart-row {
  margin-bottom:20px;
}
.recent-card {
  margin-top:0;
}
</style>
