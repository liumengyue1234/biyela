<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>CT图像松材线虫病检测系统</h1>
        <p>基于深度学习的松材线虫病智能检测与可视化系统</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
          >
            <template #prefix>
              <el-icon :size="20"><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon :size="20"><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="captcha">
          <div class="captcha-row">
            <el-input
              v-model="loginForm.captcha"
              placeholder="请输入验证码"
              size="large"
              style="flex:1"
            >
              <template #prefix>
                <el-icon :size="20"><Key /></el-icon>
              </template>
            </el-input>
            <div class="captcha-img" @click="refreshCaptcha">
              <span>{{ captchaText }}</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
           :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span @click="goRegister">没有账号？立即注册</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api'
import { User, Lock, Key } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const loginFormRef = ref()
const loading = ref(false)
const captchaText = ref('')

const loginForm = reactive({
  username: '',
  password: '',
  captcha: '',
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
}

const generateCaptcha = () => {
  const chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
  let result = ''
  for (let i = 0; i < 4; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  captchaText.value = result
}

const refreshCaptcha = () => {
  generateCaptcha()
}

const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    if (loginForm.captcha.toLowerCase() !== captchaText.value.toLowerCase()) {
      ElMessage.error('验证码错误')
      generateCaptcha()
      return
    }

    loading.value = true
    try {
      const res = await userApi.login({
        username: loginForm.username,
        password: loginForm.password
      })
      if (res.code === 200) {
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('userInfo', JSON.stringify(res.data.userInfo))
        ElMessage.success('登录成功')
        router.push('/home')
      } else {
        ElMessage.error(res.message || '登录失败')
      }
    } catch (error) {
      ElMessage.error('登录失败，请稍后重试')
    } finally {
      loading.value = false
    }
  })
}

const goRegister = () => {
  router.push('/register')
}

onMounted(() => {
  generateCaptcha()
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 450px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 10px;
}

.login-header p {
  font-size: 14px;
  color: #909399;
}

.captcha-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.captcha-img {
  width: 120px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 20px;
  font-weight: bold;
  letter-spacing: 4px;
  color: #409eff;
  user-select: none;
}

.login-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #409eff;
  cursor: pointer;
}

.login-footer span:hover {
  color: #66b1ff;
}
</style>
