import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      if (res.code === 401) {
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  error => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

// ======================== 用户相关API ========================
export const userApi = {
  login: (data) => request.post('/user/login', data),
  register: (data) => request.post('/user/register', data),
  getUserInfo: () => request.get('/user/info'),
  updateUserInfo: (data) => request.put('/user/info', data),
  changePassword: (data) => request.put('/user/password', data),
  getUserList: (params) => request.get('/user/list', { params }),
  deleteUser: (id) => request.delete(`/user/${id}`),
  updateUser: (id, data) => request.put(`/user/${id}`, data),
}

// ======================== CT影像相关API ========================
export const imageApi = {
  uploadImage: (formData) => request.post('/image/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getImageList: (params) => request.get('/image/list', { params }),
  deleteImage: (id) => request.delete(`/image/${id}`),
  getImageDetail: (id) => request.get(`/image/${id}`),
}

// ======================== 检测相关API ========================
export const detectionApi = {
  startDetection: (data) => request.post('/detection/start', data),
  getDetectionResult: (id) => request.get(`/detection/result/${id}`),
  getDetectionHistory: (params) => request.get('/detection/history', { params }),
  getDetectionDetail: (id) => request.get(`/detection/${id}`),
}

// ======================== 报告相关API ========================
export const reportApi = {
  generateReport: (detectionId) => request.post(`/report/generate/${detectionId}`),
  getReportList: (params) => request.get('/report/list', { params }),
  getReportDetail: (id) => request.get(`/report/${id}`),
  downloadReport: (id) => request.get(`/report/download/${id}`, { responseType: 'blob' }),
}

// ======================== 模型对比API ========================
export const modelApi = {
  getModelComparison: () => request.get('/model/comparison'),
  getModelDetail: (modelName) => request.get(`/model/detail/${modelName}`),
}

export default request
