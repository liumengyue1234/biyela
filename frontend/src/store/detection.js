import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { detectionApi, imageApi } from '@/api'

export const useDetectionStore = defineStore('detection', () => {
  // 检测状态
  const detecting = ref(false)
  const currentResult = ref(null)
  const detectionHistory = ref([])
  const historyTotal = ref(0)
  const historyParams = reactive({
    page: 1,
    pageSize: 10,
    modelName: '',
    startDate: '',
    endDate: '',
  })

  // 开始检测
  const startDetection = async (formData) => {
    detecting.value = true
    try {
      const res = await detectionApi.startDetection(formData)
      if (res.code === 200) {
        currentResult.value = res.data
      }
      return res
    } finally {
      detecting.value = false
    }
  }

  // 获取检测结果
  const fetchDetectionResult = async (id) => {
    const res = await detectionApi.getDetectionResult(id)
    if (res.code === 200) {
      currentResult.value = res.data
    }
    return res
  }

  // 获取检测历史
  const fetchHistory = async () => {
    const res = await detectionApi.getDetectionHistory(historyParams)
    if (res.code === 200) {
      detectionHistory.value = res.data.records || res.data.list || []
      historyTotal.value = res.data.total || 0
    }
    return res
  }

  // 获取检测详情
  const fetchDetectionDetail = async (id) => {
    const res = await detectionApi.getDetectionDetail(id)
    return res
  }

  // 重置结果
  const resetResult = () => {
    currentResult.value = null
  }

  // 重置历史参数
  const resetHistoryParams = () => {
    historyParams.page = 1
    historyParams.pageSize = 10
    historyParams.modelName = ''
    historyParams.startDate = ''
    historyParams.endDate = ''
  }

  return {
    detecting,
    currentResult,
    detectionHistory,
    historyTotal,
    historyParams,
    startDetection,
    fetchDetectionResult,
    fetchHistory,
    fetchDetectionDetail,
    resetResult,
    resetHistoryParams,
  }
})
