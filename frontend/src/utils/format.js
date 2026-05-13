/**
 * 格式化工具函数
 */

/**
 * 格式化日期时间
 * @param {string|Date} date 日期
 * @param {string} format 格式类型
 * @returns {string}
 */
export function formatDateTime(date, format = 'datetime') {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  switch (format) {
    case 'date':
      return `${year}-${month}-${day}`
    case 'time':
      return `${hours}:${minutes}:${seconds}`
    case 'datetime':
    default:
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }
}

/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string}
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + units[i]
}

/**
 * 格式化百分比
 * @param {number} value 数值 (0-1)
 * @param {number} digits 小数位数
 * @returns {string}
 */
export function formatPercent(value, digits = 2) {
  if (value === null || value === undefined) return '--'
  return (value * 100).toFixed(digits) + '%'
}

/**
 * 格式化指标数值
 * @param {number} value 数值 (0-1)
 * @param {number} digits 小数位数
 * @returns {string}
 */
export function formatMetric(value, digits = 4) {
  if (value === null || value === undefined) return '--'
  return value.toFixed(digits)
}

/**
 * 格式化检测状态
 * @param {string} status 状态码
 * @returns {string}
 */
export function formatDetectionStatus(status) {
  const statusMap = {
    pending: '等待中',
    processing: '检测中',
    completed: '已完成',
    failed: '失败',
  }
  return statusMap[status] || status
}

/**
 * 获取检测状态标签类型
 * @param {string} status 状态码
 * @returns {string}
 */
export function getStatusType(status) {
  const typeMap = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return typeMap[status] || 'info'
}

/**
 * 格式化模型名称
 * @param {string} modelKey 模型标识
 * @returns {string}
 */
export function formatModelName(modelKey) {
  const nameMap = {
    improved_unet: '改进U-Net (CBAM+残差+多尺度)',
    standard_unet: '标准U-Net',
    mask_rcnn: 'Mask R-CNN',
    yolov8: 'YOLOv8',
    yolov10: 'YOLOv10',
    yolov11: 'YOLOv11',
  }
  return nameMap[modelKey] || modelKey
}

/**
 * 格式化去噪方法名称
 * @param {string} method 去噪方法标识
 * @returns {string}
 */
export function formatDenoiseMethod(method) {
  const methodMap = {
    bilateral: '双边滤波',
    gaussian: '高斯滤波',
    median: '中值滤波',
    nlmeans: '非局部均值',
    none: '不去噪',
  }
  return methodMap[method] || method
}

/**
 * 生成唯一ID
 * @returns {string}
 */
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 9)
}

/**
 * 防抖函数
 * @param {Function} fn 目标函数
 * @param {number} delay 延迟毫秒数
 * @returns {Function}
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}
