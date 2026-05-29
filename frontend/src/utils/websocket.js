import { ElMessage } from 'element-plus'

let ws = null
let lockReconnect = false
let retryCount = 0
let authFailed = false
const MAX_RETRY = 10

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

function createWebSocket() {
  const token = localStorage.getItem('token')
  if (!token) return

  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsHost = API_BASE ? API_BASE.replace(/^http/, 'ws') : `${wsProtocol}//${window.location.host}`
  const wsUrl = `${wsHost}/api/ws`
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('✅ WebSocket 已连接！')
    retryCount = 0
    authFailed = false
    ws.send(JSON.stringify({ type: 'auth', token: localStorage.getItem('token') }))
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)

      if (data.type === 'auth') {
        if (data.status === 'ok') {
          console.log('✅ WebSocket 认证成功')
        } else {
          console.warn('❌ WebSocket 认证失败:', data.msg)
          authFailed = true
          ws.close()
        }
        return
      }

      if (data.type === 'door_open') {
        const role = localStorage.getItem('role')
        if (role === 'admin') {
          ElMessage.success(data.message)
        }
      }
    } catch (e) {
      console.log('消息解析失败', e)
    }
  }

  ws.onerror = () => reconnect()
  ws.onclose = () => {
    console.log('❌ WebSocket 断开')
    reconnect()
  }
}

function reconnect() {
  // 认证失败后不重连（避免死循环）
  if (authFailed) return
  if (lockReconnect) return
  if (retryCount >= MAX_RETRY) {
    console.log('WebSocket 重连已达上限')
    return
  }
  lockReconnect = true
  retryCount++
  console.log(`WebSocket 重连中 (${retryCount}/${MAX_RETRY})...`)
  setTimeout(() => {
    createWebSocket()
    lockReconnect = false
  }, 2000)
}

export function initWebSocket() {
  createWebSocket()
}

export default { initWebSocket }
