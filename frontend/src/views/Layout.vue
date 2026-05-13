<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="aside-logo">
        <img v-if="!isCollapse" src="/vite.svg" alt="logo" class="logo-img" />
        <img v-else src="/vite.svg" alt="logo" class="logo-img-small" />
        <span v-if="!isCollapse" class="logo-text">松材线虫检测</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
        background-color="#001529"
        text-color="#ffffffa6"
        active-text-color="#ffffff"
        class="aside-menu"
      >
        <el-menu-item index="/home">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>

        <el-menu-item index="/detection">
          <el-icon><PictureFilled /></el-icon>
          <template #title>CT影像检测</template>
        </el-menu-item>

        <el-menu-item index="/images">
          <el-icon><FolderOpened /></el-icon>
          <template #title>CT影像管理</template>
        </el-menu-item>

        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <template #title>历史检测记录</template>
        </el-menu-item>

        <el-menu-item index="/report">
          <el-icon><Document /></el-icon>
          <template #title>检测报告</template>
        </el-menu-item>

        <el-menu-item index="/model-compare">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>模型对比</template>
        </el-menu-item>

        <el-menu-item v-if="isAdmin" index="/users">
          <el-icon><UserFilled /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>

        <el-menu-item index="/profile">
          <el-icon><Setting /></el-icon>
          <template #title>个人中心</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon
            :size="20"
            class="collapse-btn"
            @click="isCollapse = !isCollapse"
          >
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32">{{ userInfo?.username?.charAt(0)?.toUpperCase() }}</el-avatar>
              <span class="username">{{ userInfo?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  HomeFilled, PictureFilled, FolderOpened, Clock,
  Document, DataAnalysis, UserFilled, Setting,
  Fold, Expand, ArrowDown
} from '@element-plus/icons-vue'
import { userApi } from '@/api'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)
const userInfo = ref(null)

const isAdmin = computed(() => {
  return userInfo.value?.role === 'admin'
})

const currentTitle = computed(() => {
  return route.meta.title || '首页'
})

const activeMenu = computed(() => {
  return route.path
})

const fetchUserInfo = async () => {
  try {
    const res = await userApi.getUserInfo()
    if (res.code === 200) {
      userInfo.value = res.data
    }
  } catch (e) {
    console.error('获取用户信息失败', e)
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-aside {
  background-color: #001529;
  transition: width 0.3s;
  overflow: hidden;
}

.aside-logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid #ffffff1a;
}

.logo-img {
  width: 32px;
  height: 32px;
}

.logo-img-small {
  width: 32px;
  height: 32px;
}

.logo-text {
  color: white;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.aside-menu {
  border-right: none;
}

.layout-header {
  background: white;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  cursor: pointer;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #303133;
}

.username {
  font-size: 14px;
}

.layout-main {
  background-color: #f0f2f5;
  min-height: 0;
}
</style>
