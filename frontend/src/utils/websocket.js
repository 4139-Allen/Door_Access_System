import { ElMessage } from 'element-plus'

let ws = null
let lockReconnect = false
let retryCount = 0
const MAX_RETRY = 10

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

function createWebSocket() {
  const token = localStorage.getItem('token')
  if (!token) return

  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsHost = API_BASE ? API_BASE.replace(/^http/, 'ws') : `${wsProtocol}//${window.location.host}`
  const wsUrl = `${wsHost}/api/ws?token=${token}`
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('✅ WebSocket 已连接！')
    retryCount = 0
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      const role = localStorage.getItem('role')

      if (data.type === 'door_open' && role === 'admin') {
        ElMessage.success(data.message)
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
