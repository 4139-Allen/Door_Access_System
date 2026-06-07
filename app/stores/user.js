export function getToken() {
  return uni.getStorageSync('token') || ''
}

export function getRole() {
  return uni.getStorageSync('role') || ''
}

export function getUsername() {
  return uni.getStorageSync('username') || ''
}

export function isLoggedIn() {
  return !!uni.getStorageSync('token')
}

export function isAdmin() {
  return uni.getStorageSync('role') === 'admin'
}

export function saveLoginInfo(token, role, username) {
  uni.setStorageSync('token', token)
  uni.setStorageSync('role', role)
  if (username) uni.setStorageSync('username', username)
}

export function clearLoginInfo() {
  uni.removeStorageSync('token')
  uni.removeStorageSync('role')
  uni.removeStorageSync('username')
}
