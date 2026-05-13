<template>
  <div class="profile">
    <el-row :gutter="20">
      <!-- 左侧个人信息卡片 -->
      <el-col :span="8">
        <el-card>
          <div class="avatar-container">
            <el-avatar :size="120" :src="userInfo.avatar">
              {{ userInfo.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <h3>{{ userInfo.username }}</h3>
            <el-tag :type="userInfo.role === 'admin' ? 'danger' : 'primary'">
              {{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </div>

          <el-divider />

          <div class="info-list">
            <div class="info-item">
              <el-icon><Message /></el-icon>
              <span>{{ userInfo.email || '未设置邮箱' }}</span>
            </div>
            <div class="info-item">
              <el-icon><Phone /></el-icon>
              <span>{{ userInfo.phone || '未设置手机号' }}</span>
            </div>
            <div class="info-item">
              <el-icon><Clock /></el-icon>
              <span>注册时间：{{ userInfo.createTime || '-' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧标签页 -->
      <el-col :span="16">
        <el-card>
          <el-tabs v-model="activeTab">
            <!-- 基本资料 -->
            <el-tab-pane label="基本资料" name="basic">
              <el-form
                ref="basicFormRef"
                :model="basicForm"
                :rules="basicRules"
                label-width="100px"
                style="max-width: 500px; margin: 20px auto;"
              >
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="basicForm.username" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="basicForm.email" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="basicForm.phone" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="submitBasicForm">
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 修改密码 -->
            <el-tab-pane label="修改密码" name="password">
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="100px"
                style="max-width: 500px; margin: 20px auto;"
              >
                <el-form-item label="原密码" prop="oldPassword">
                  <el-input
                    v-model="passwordForm.oldPassword"
                    type="password"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="新密码" prop="newPassword">
                  <el-input
                    v-model="passwordForm.newPassword"
                    type="password"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input
                    v-model="passwordForm.confirmPassword"
                    type="password"
                    show-password
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="submitPasswordForm">
                    修改密码
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 检测统计 -->
            <el-tab-pane label="检测统计" name="statistics">
              <div ref="statsChartRef" style="width: 100%; height: 400px;" />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi } from '../api'
import * as echarts from 'echarts'

const activeTab = ref('basic')
const basicFormRef = ref()
const passwordFormRef = ref()
const statsChartRef = ref(null)

const userInfo = reactive({
  id: '',
  username: '',
  email: '',
  phone: '',
  role: '',
  avatar: '',
  createTime: ''
})

const basicForm = reactive({
  username: '',
  email: '',
  phone: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const basicRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

onMounted(() => {
  getUserInfo()
})

const getUserInfo = async () => {
  try {
    const res = await userApi.getProfile()
    Object.assign(userInfo, res.data)
    Object.assign(basicForm, res.data)
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
}

const submitBasicForm = () => {
  basicFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await userApi.updateProfile(basicForm)
        ElMessage.success('保存成功')
        getUserInfo()
      } catch (error) {
        ElMessage.error('保存失败')
      }
    }
  })
}

const submitPasswordForm = () => {
  passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await userApi.changePassword(passwordForm)
        ElMessage.success('密码修改成功')
        passwordForm.oldPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
      } catch (error) {
        ElMessage.error('密码修改失败')
      }
    }
  })
}

// 监听标签页切换
const handleTabChange = (tab) => {
  if (tab === 'statistics') {
    nextTick(() => {
      initStatsChart()
    })
  }
}

const initStatsChart = () => {
  if (!statsChartRef.value) return
  const chart = echarts.init(statsChartRef.value)

  const option = {
    title: {
      text: '检测统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['检测次数', '阳性数量', '阴性数量'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '检测次数',
        type: 'bar',
        data: [12, 20, 15, 25, 30, 22]
      },
      {
        name: '阳性数量',
        type: 'line',
        data: [3, 5, 4, 8, 10, 7]
      },
      {
        name: '阴性数量',
        type: 'line',
        data: [9, 15, 11, 17, 20, 15]
      }
    ]
  }

  chart.setOption(option)
}
</script>

<style scoped>
.profile {
  padding: 20px;
}

.avatar-container {
  text-align: center;
  padding: 20px 0;
}

.avatar-container h3 {
  margin: 15px 0 10px 0;
}

.info-list {
  padding: 0 20px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  color: #606266;
}

.info-item .el-icon {
  margin-right: 10px;
  font-size: 18px;
  color: #409eff;
}
</style>
