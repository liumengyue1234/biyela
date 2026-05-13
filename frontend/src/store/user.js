import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))
  const roles = ref(JSON.parse(localStorage.getItem('roles') || '[]'))

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => roles.value.includes('admin'))
  const username = computed(() => userInfo.value.username || '')

  // 登录
  const login = async (loginForm) => {
    const res = await userApi.login(loginForm)
    if (res.code === 200) {
      token.value = res.data.token
      userInfo.value = res.data.user || {}
      roles.value = res.data.roles || ['user']
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('userInfo', JSON.stringify(res.data.user || {}))
      localStorage.setItem('roles', JSON.stringify(res.data.roles || ['user']))
    }
    return res
  }

  // 注册
  const register = async (registerForm) => {
    const res = await userApi.register(registerForm)
    return res
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      const res = await userApi.getUserInfo()
      if (res.code === 200) {
        userInfo.value = res.data
        localStorage.setItem('userInfo', JSON.stringify(res.data))
      }
    } catch (e) {
      console.warn('获取用户信息失败', e)
    }
  }

  // 退出登录
  const logout = () => {
    token.value = ''
    userInfo.value = {}
    roles.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('roles')
  }

  return {
    token,
    userInfo,
    roles,
    isLoggedIn,
    isAdmin,
    username,
    login,
    register,
    fetchUserInfo,
    logout,
  }
})
