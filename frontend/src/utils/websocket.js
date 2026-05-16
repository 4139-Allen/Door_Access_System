import { ElMessage } from 'element-plus'

let ws = null
let lockReconnect = false

function createWebSocket() {
  const wsUrl = `ws://${window.location.host}/ws`
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('✅ WebSocket 已连接！')
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      const role = localStorage.getItem('role')
      console.log('📩 收到消息：', data) // 👈 强制看日志！

      // 只要是管理员，全部显示！包括自己
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
  lockReconnect = true
  setTimeout(() => {
    createWebSocket()
    lockReconnect = false
  }, 2000)
}

export function initWebSocket() {
  createWebSocket()
}

export default { initWebSocket }