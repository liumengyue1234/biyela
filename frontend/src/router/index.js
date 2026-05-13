import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/Home.vue'),
        meta: { title: '系统首页' }
      },
      {
        path: 'detection',
        name: 'Detection',
        component: () => import('../views/Detection.vue'),
        meta: { title: '松材线虫病检测' }
      },
      {
        path: 'images',
        name: 'ImageManage',
        component: () => import('../views/ImageManage.vue'),
        meta: { title: 'CT影像管理' }
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('../views/History.vue'),
        meta: { title: '历史检测记录' }
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('../views/Report.vue'),
        meta: { title: '检测报告' }
      },
      {
        path: 'model-compare',
        name: 'ModelCompare',
        component: () => import('../views/ModelCompare.vue'),
        meta: { title: '模型对比' }
      },
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('../views/UserManage.vue'),
        meta: { title: '用户管理', requireAdmin: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { title: '个人中心' }
      },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && to.path !== '/register' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
