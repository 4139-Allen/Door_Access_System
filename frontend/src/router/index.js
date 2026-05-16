import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: () => import('../views/Login.vue') },
  {
    path: '/admin',
    component: () => import('../views/Layout.vue'),
    redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'user', component: () => import('../views/Users.vue') },
      { path: 'device', component: () => import('../views/Device.vue') },
      { path: 'log', component: () => import('../views/Log.vue') },
      { path: 'door', component: () => import('../views/Door.vue') }
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
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router