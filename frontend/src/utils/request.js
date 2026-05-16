import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service = axios.create({
  baseURL: '/api',      //baseURL: '/api'  → 交给 Nginx 转发(本地开发：'http://127.0.0.1:8000'; docker容器化：'/api')
  timeout: 15000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截
service.interceptors.response.use(
  (res) => res.data,
  (error) => {
    // 处理 HTTP 错误状态码
    if (error.response) {
      const status = error.response.status

      if (status === 401) {
        // Token 过期或无效
        ElMessage.error('登录已过期，请重新登录')
        localStorage.removeItem('token')
        localStorage.removeItem('role')
        router.push('/login')
      } else if (status === 403) {
        // 权限不足
        ElMessage.error('无权限访问')
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在')
      } else if (status >= 500) {
        ElMessage.error('服务器错误，请稍后重试')
      }
    } else {
      // 网络错误
      ElMessage.error('网络连接失败，请检查网络')
    }

    return Promise.reject(error)
  }
)

export default service
