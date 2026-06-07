import { getToken } from './auth'
import { WS_URL } from './config'

let socketTask = null
let connected = false
let reconnectCount = 0
const MAX_RECONNECT = 10
const messageHandlers = []

export function connectWebSocket() {
  if (connected || socketTask) return

  socketTask = uni.connectSocket({
    url: `${WS_URL}/api/ws`,
    success() {},
    fail() {}
  })

  uni.onSocketOpen(() => {
    connected = true
    reconnectCount = 0
    const token = getToken()
    if (token) {
      uni.sendSocketMessage({
        data: JSON.stringify({ type: 'auth', token })
      })
    }
  })

  uni.onSocketMessage((res) => {
    try {
      const msg = JSON.parse(res.data)
      if (msg.type === 'auth' && msg.status === 'failed') {
        disconnectWebSocket()
        return
      }
      messageHandlers.forEach(handler => handler(msg))
    } catch (e) {}
  })

  uni.onSocketClose(() => {
    connected = false
    socketTask = null
    if (reconnectCount < MAX_RECONNECT) {
      const delay = Math.min(1000 * Math.pow(2, reconnectCount), 30000)
      reconnectCount++
      setTimeout(() => connectWebSocket(), delay)
    }
  })

  uni.onSocketError(() => {
    connected = false
    socketTask = null
  })
}

export function disconnectWebSocket() {
  if (socketTask) {
    uni.closeSocket()
    socketTask = null
    connected = false
  }
}

export function onSocketMessage(handler) {
  messageHandlers.push(handler)
}

export function offSocketMessage(handler) {
  const idx = messageHandlers.indexOf(handler)
  if (idx > -1) messageHandlers.splice(idx, 1)
}
