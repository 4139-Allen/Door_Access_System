<template>
  <el-container class="layout-container">
    <!-- 桌面端侧边栏 -->
    <SidebarMenu :role="role" class="desktop-sidebar" @change-password="showPasswordDialog = true" @logout="logout" />

    <!-- 移动端侧边栏 Overlay -->
    <Teleport to="body">
      <Transition name="sidebar-fade">
        <div v-if="sidebarOpen" class="mobile-sidebar-overlay" @click="sidebarOpen = false">
          <div class="mobile-sidebar-panel" @click.stop>
            <SidebarMenu :role="role" @navigate="sidebarOpen = false" @change-password="showPasswordDialog = true; sidebarOpen = false" @logout="logout" />
          </div>
        </div>
      </Transition>
    </Teleport>

    <el-container class="main-container">
      <!-- 顶部栏 -->
      <el-header class="app-header">
        <div class="header-left">
          <el-button text class="hamburger-btn" @click="sidebarOpen = true">
            <el-icon :size="20"><Fold /></el-icon>
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main class="app-main">
        <router-view v-slot="{ Component, route }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>

  <!-- 修改密码弹窗 -->
  <ChangePasswordModal
    v-model:show="showPasswordDialog"
    :form="passwordForm"
    :rules="passwordRules"
    :loading="changing"
    @cancel="showPasswordDialog = false"
    @confirm="handleChangePassword"
    ref="passwordModal"
  />
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ref, reactive, computed, watch } from 'vue'
import { Fold } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { closeWebSocket } from '@/utils/websocket'
import SidebarMenu from '@/components/Layout/SidebarMenu.vue'
import ChangePasswordModal from '@/components/Layout/ChangePasswordModal.vue'

const router = useRouter()
const route = useRoute()
const role = ref(localStorage.getItem('role') || '')
const showPasswordDialog = ref(false)
const changing = ref(false)
const passwordModal = ref(null)
const sidebarOpen = ref(false)

// 路由变化时关闭移动端侧边栏
watch(() => route.path, () => { sidebarOpen.value = false })

const pageNames = {
  '/admin/dashboard': '仪表盘',
  '/admin/door': '用户开门',
  '/admin/user': '用户管理',
  '/admin/device': '设备管理',
  '/admin/log': '门禁日志',
  '/user/dashboard': '仪表盘',
  '/user/door': '用户开门',
}

const currentPageName = computed(() => pageNames[route.path] || '')

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) callback(new Error('请确认新密码'))
  else if (value !== passwordForm.new_password) callback(new Error('两次密码不一致'))
  else callback()
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }, { min: 6 }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6 }],
  confirm_password: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }]
}

const handleChangePassword = async () => {
  const modal = passwordModal.value
  if (!modal) return
  const formRef = modal.passwordFormRef
  if (!formRef) return

  await formRef.validate(async (valid) => {
    if (!valid) return
    changing.value = true
    try {
      const res = await request.put('/auth/password', {
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      })
      if (res.code === 200) {
        ElMessage.success('密码修改成功，请重新登录')
        showPasswordDialog.value = false
        passwordForm.old_password = ''
        passwordForm.new_password = ''
        passwordForm.confirm_password = ''
        setTimeout(logout, 500)
      } else {
        ElMessage.error(res.msg || '修改失败')
      }
    } catch (err) {
      ElMessage.error(err.response?.data?.msg || '修改失败')
    } finally {
      changing.value = false
    }
  })
}

const logout = async () => {
  closeWebSocket()
  try {
    await request.post('/auth/logout')
  } catch {
    // 忽略退出登录的接口错误
  }
  localStorage.clear()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background: #f1f5f9;
}

.main-container {
  display: flex;
  flex-direction: column;
}

/* ======== 顶部栏 ======== */
.app-header {
  height: 56px !important;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 28px !important;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-left :deep(.el-breadcrumb__inner) {
  font-size: 14px;
}

.header-left :deep(.el-breadcrumb__inner.is-link) {
  color: #64748b;
  font-weight: 400;
}

.header-left :deep(.el-breadcrumb__inner.is-link:hover) {
  color: #6366f1;
}

.header-left :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #1e293b;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ======== 主内容 ======== */
.app-main {
  background: #f1f5f9;
  padding: 20px 24px;
  overflow-y: auto;
  height: calc(100vh - 56px);
}

/* ======== 页面过渡动画 ======== */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* ======== 移动端适配 ======== */
.hamburger-btn {
  display: none;
  padding: 6px;
  margin-right: 8px;
}

/* 移动端侧边栏 Overlay */
.mobile-sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.4);
}

.mobile-sidebar-panel {
  position: absolute;
  left: 0;
  top: 0;
  width: 220px;
  height: 100%;
}

/* Overlay 动画 */
.sidebar-fade-enter-active,
.sidebar-fade-leave-active {
  transition: opacity 0.25s ease;
}
.sidebar-fade-enter-active .mobile-sidebar-panel,
.sidebar-fade-leave-active .mobile-sidebar-panel {
  transition: transform 0.25s ease;
}
.sidebar-fade-enter-from,
.sidebar-fade-leave-to {
  opacity: 0;
}
.sidebar-fade-enter-from .mobile-sidebar-panel,
.sidebar-fade-leave-to .mobile-sidebar-panel {
  transform: translateX(-100%);
}

@media (max-width: 768px) {
  .desktop-sidebar {
    display: none;
  }
  .mobile-sidebar-overlay {
    display: flex;
  }
  .hamburger-btn {
    display: flex;
  }
  .app-header {
    padding: 0 16px !important;
  }
  .app-main {
    padding: 12px;
  }
}
</style>
