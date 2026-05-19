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
      { path: 'door', component: () => import('../views/Door.vue') },
      { path: 'user', component: () => import('../views/Users.vue'), meta: { role: 'admin' } },
      { path: 'device', component: () => import('../views/Device.vue'), meta: { role: 'admin' } },
      { path: 'log', component: () => import('../views/Log.vue'), meta: { role: 'admin' } }
    ]
  },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('../views/NotFound.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (to.path !== '/login' && !token) {
    next('/login')
    return
  }

  if (to.path === '/login' && token) {
    next('/admin/dashboard')
    return
  }

  if (to.meta?.role && role !== to.meta.role) {
    next('/admin/dashboard')
    return
  }

  next()
})

export default router
