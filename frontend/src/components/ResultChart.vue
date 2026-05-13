<template>
  <div class="result-chart">
    <!-- 指标数值展示 -->
    <div v-if="metrics && showMetrics" class="metrics-display">
      <div
        v-for="item in metricItems"
        :key="item.key"
        class="metric-card"
        :style="{ borderColor: item.color }"
      >
        <div class="metric-label">{{ item.label }}</div>
        <div class="metric-value" :style="{ color: item.color }">
          {{ formatValue(metrics[item.key]) }}
        </div>
      </div>
    </div>

    <!-- ECharts 图表 -->
    <div v-if="chartType" ref="chartRef" class="chart-container" :style="{ height: chartHeight }"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  // 检测结果数据
  metrics: {
    type: Object,
    default: () => ({}),
  },
  // 模型对比数据
  comparisonData: {
    type: Array,
    default: () => [],
  },
  // 图表类型：bar(柱状图), radar(雷达图), line(折线图)
  chartType: {
    type: String,
    default: '',
  },
  // 是否显示指标数值
  showMetrics: {
    type: Boolean,
    default: true,
  },
  // 图表高度
  chartHeight: {
    type: String,
    default: '350px',
  },
})

const chartRef = ref(null)
let chartInstance = null

const metricItems = computed(() => [
  { key: 'dice', label: 'Dice系数', color: '#409eff' },
  { key: 'iou', label: 'IoU', color: '#67c23a' },
  { key: 'precision', label: '精确率', color: '#e6a23c' },
  { key: 'recall', label: '召回率', color: '#f56c6c' },
  { key: 'f1', label: 'F1分数', color: '#909399' },
  { key: 'accuracy', label: '准确率', color: '#b37feb' },
])

const formatValue = (val) => {
  if (val === null || val === undefined) return '--'
  return (val * 100).toFixed(2) + '%'
}

const initChart = () => {
  if (!chartRef.value || !props.chartType) return

  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance) return

  let option = {}

  if (props.chartType === 'bar' && props.comparisonData.length > 0) {
    option = getBarOption()
  } else if (props.chartType === 'radar' && props.comparisonData.length > 0) {
    option = getRadarOption()
  } else if (props.chartType === 'line') {
    option = getLineOption()
  }

  chartInstance.setOption(option, true)
}

const getBarOption = () => {
  const models = props.comparisonData.map(d => d.modelName || d.model)
  const metricKeys = ['dice', 'iou', 'precision', 'recall', 'f1']
  const metricNames = ['Dice', 'IoU', '精确率', '召回率', 'F1']
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']

  return {
    title: { text: '模型性能对比', left: 'center' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: models },
    yAxis: { type: 'value', max: 1, axisLabel: { formatter: '{value}' } },
    series: metricKeys.map((key, i) => ({
      name: metricNames[i],
      type: 'bar',
      data: props.comparisonData.map(d => d[key] ?? 0),
      itemStyle: { color: colors[i] },
    })),
  }
}

const getRadarOption = () => {
  const indicators = [
    { name: 'Dice', max: 1 },
    { name: 'IoU', max: 1 },
    { name: '精确率', max: 1 },
    { name: '召回率', max: 1 },
    { name: 'F1', max: 1 },
  ]
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']

  return {
    title: { text: '模型雷达图对比', left: 'center' },
    tooltip: {},
    legend: { bottom: 0, data: props.comparisonData.map(d => d.modelName || d.model) },
    radar: { indicator: indicators, center: ['50%', '50%'] },
    series: [{
      type: 'radar',
      data: props.comparisonData.map((d, i) => ({
        name: d.modelName || d.model,
        value: [d.dice ?? 0, d.iou ?? 0, d.precision ?? 0, d.recall ?? 0, d.f1 ?? 0],
        itemStyle: { color: colors[i % colors.length] },
        areaStyle: { opacity: 0.2 },
      })),
    }],
  }
}

const getLineOption = () => {
  return {
    title: { text: '训练曲线', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value' },
    series: [],
  }
}

const handleResize = () => {
  chartInstance?.resize()
}

watch(() => [props.comparisonData, props.metrics, props.chartType], () => {
  nextTick(() => updateChart())
}, { deep: true })

onMounted(() => {
  nextTick(() => initChart())
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.result-chart {
  width: 100%;
}
.metrics-display {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}
.metric-card {
  flex: 1;
  min-width: 120px;
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 4px solid #ddd;
  background: #fafafa;
  text-align: center;
}
.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}
.metric-value {
  font-size: 20px;
  font-weight: bold;
}
.chart-container {
  width: 100%;
}
</style>
