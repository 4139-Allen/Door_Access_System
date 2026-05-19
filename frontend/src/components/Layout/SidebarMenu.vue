<template>
  <el-aside width="220px" class="sidebar-container">
    <!-- Logo -->
    <div class="sidebar-header">
      <div class="logo-mark">D</div>
      <div class="logo-text">
        <span class="logo-title">智能门禁</span>
        <span class="logo-sub">管理控制系统</span>
      </div>
    </div>

    <!-- 导航 -->
    <el-menu
      :default-active="activeRoute"
      background-color="transparent"
      text-color="rgba(255,255,255,0.6)"
      active-text-color="#fff"
      router
      class="sidebar-menu"
    >
      <div class="menu-label">导航</div>

      <el-menu-item index="/admin/dashboard">
        <span>首页</span>
      </el-menu-item>

      <el-menu-item index="/admin/door">
        <span>用户开门</span>
      </el-menu-item>

      <template v-if="role === 'admin'">
        <div class="menu-label">管理</div>

        <el-menu-item index="/admin/user">
          <span>用户管理</span>
        </el-menu-item>

        <el-menu-item index="/admin/device">
          <span>设备管理</span>
        </el-menu-item>

        <el-menu-item index="/admin/log">
          <span>门禁日志</span>
        </el-menu-item>
      </template>
    </el-menu>

    <!-- 底部 -->
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">{{ role === 'admin' ? 'A' : 'U' }}</div>
        <div class="user-meta">
          <span class="user-name">{{ role === 'admin' ? '管理员' : '普通用户' }}</span>
          <span class="user-role">{{ role === 'admin' ? 'Admin' : 'User' }}</span>
        </div>
      </div>
    </div>
  </el-aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

defineProps({ role: String })
const route = useRoute()
const activeRoute = computed(() => route.path)
</script>

<style scoped>
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1e293b;
  user-select: none;
}

/* ======== Logo ======== */
.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.logo-mark {
  width: 36px;
  height: 36px;
  background: #6366f1;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.logo-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
  line-height: 1.3;
}

.logo-sub {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  line-height: 1.3;
}

/* ======== 菜单 ======== */
.sidebar-menu {
  flex: 1;
  border-right: none;
  padding: 8px 12px;
  overflow-y: auto;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 100%;
}

.menu-label {
  padding: 20px 12px 6px;
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.25);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.el-menu-item {
  border-radius: 6px;
  margin: 2px 0;
  height: 40px !important;
  line-height: 40px !important;
  padding: 0 12px !important;
  font-size: 14px;
}

.el-menu-item:hover {
  background: rgba(255, 255, 255, 0.06) !important;
  color: rgba(255, 255, 255, 0.9) !important;
}

.el-menu-item.is-active {
  background: rgba(99, 102, 241, 0.15) !important;
  color: #fff !important;
}

/* ======== 底部 ======== */
.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: #6366f1;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.3;
}

.user-role {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  line-height: 1.3;
}

/* 滚动条 */
.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}
</style>
