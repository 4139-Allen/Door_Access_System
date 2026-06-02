<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <el-card class="welcome-banner" shadow="never">
      <div class="welcome-content">
        <div class="welcome-left">
          <div class="greeting-line">
            <span class="greeting-text">{{ greetingText }}，</span>
            <span class="greeting-role">{{ roleLabel }}</span>
          </div>
          <p class="welcome-sub">{{ todaySub }}</p>
        </div>
        <div class="welcome-right">
          <div class="date-text">{{ dateStr }}</div>
          <div class="time-text">{{ timeStr }}</div>
        </div>
      </div>
    </el-card>

    <!-- 统计 -->
    <el-row :gutter="20" class="stat-row">
      <StatCard
        v-if="role === 'admin'"
        title="用户总数"
        :number="stat.user_total"
        color="#409eff"
      />
      <StatCard
        :title="role === 'admin' ? '设备总数' : '我的设备数'"
        :number="stat.device_total"
        color="#67c23a"
      />
      <StatCard
        :title="role === 'admin' ? '今日开门记录' : '我的今日开门记录'"
        :number="stat.today_log"
        color="#e6a23c"
      />
    </el-row>

    <!-- 快捷操作 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <span class="section-title">快捷操作</span>
      </template>
      <div class="quick-actions">
        <el-button class="action-btn" @click="goRoute(routePrefix + '/door')">快速开门</el-button>
        <el-button v-if="role === 'admin'" class="action-btn" @click="goRoute(routePrefix + '/device')">设备管理</el-button>
        <el-button v-if="role === 'admin'" class="action-btn" @click="goRoute(routePrefix + '/log')">查看日志</el-button>
        <el-button v-if="role === 'admin'" class="action-btn" @click="goRoute(routePrefix + '/user')">用户管理</el-button>
      </div>
    </el-card>

    <!-- 实时事件流 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="section-header">
          <span class="section-title">实时事件流</span>
          <el-tag v-if="eventList.length > 0" type="success" size="small" effect="plain">
            共 {{ eventList.length }} 条
          </el-tag>
        </div>
      </template>
      <div class="event-stream" v-loading="logsLoading">
        <TransitionGroup name="event-slide" tag="div">
          <div
            v-for="event in displayedEvents"
            :key="event.id"
            class="event-item"
          >
            <div class="event-dot"></div>
            <div class="event-body">
              <div class="event-main">
                <span class="event-user">{{ event.username }}</span>
                <span class="event-sep">打开了</span>
                <span class="event-device">{{ event.device_name }}</span>
                <span v-if="event.location" class="event-location">({{ event.location }})</span>
              </div>
              <div class="event-meta">
                <el-tag size="small" :type="actionTagType(event.action)" effect="plain">
                  {{ event.action }}
                </el-tag>
                <span class="event-time">{{ event.timestamp }}</span>
              </div>
            </div>
          </div>
        </TransitionGroup>
        <div v-if="displayedEvents.length === 0 && !logsLoading" class="event-empty">
          暂无事件
        </div>
      </div>
    </el-card>

    <!-- AI 悬浮按钮 -->
    <div class="ai-fab-wrap" @click="aiDialog = true">
      <button class="ai-fab">AI</button>
    </div>

    <AiChatBox v-model:visible="aiDialog" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import StatCard from '@/components/Dashboard/StatCard.vue'
import AiChatBox from '@/components/Dashboard/AiChatBox.vue'
import { useDoorEventStream } from '@/composables/useDoorEventStream'

const router = useRouter()
const role = ref(localStorage.getItem('role') || '')
const aiDialog = ref(false)
const logsLoading = ref(false)

// 根据角色生成路由前缀
const routePrefix = computed(() => role.value === 'admin' ? '/admin' : '/user')

const stat = ref({ user_total: 0, device_total: 0, today_log: 0 })
const recentLogs = ref([])
const { eventList, addDoorEvent } = useDoorEventStream()
const displayedEvents = computed(() => eventList.slice(0, 20))

const actionTagType = (action) => {
  if (action.includes('密码')) return 'warning'
  if (action.includes('指纹')) return 'success'
  if (action.includes('刷卡')) return 'primary'
  return 'info'
}

watch(
  () => eventList.length,
  (newLen, oldLen) => {
    if (newLen > oldLen) {
      stat.value.today_log += (newLen - oldLen)
    }
  }
)

const now = ref(new Date())
let timer = null

const days = ['日', '一', '二', '三', '四', '五', '六']

const dateStr = computed(() => {
  const d = now.value
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 星期${days[d.getDay()]}`
})

const timeStr = computed(() => {
  const d = now.value
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
})

const roleLabel = computed(() => role.value === 'admin' ? '管理员' : '用户')

const greetingText = computed(() => {
  const h = now.value.getHours()
  if (h < 6) return '夜深了，注意休息'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const todaySub = computed(() => {
  const count = stat.value.today_log
  return role.value === 'admin'
    ? `今日共有 ${count} 条开门记录`
    : `今日您有 ${count} 条开门记录`
})

const getStat = async () => {
  try {
    const res = await request.get('/statistics')
    if (res.code === 200) stat.value = res.data
  } catch (e) {
    console.error('获取统计失败', e)
  }
}

const getRecentLogs = async () => {
  logsLoading.value = true
  try {
    const res = await request.get('/door-logs', {
      params: { page: 1, size: 5 }
    })
    if (res.code === 200) {
      recentLogs.value = res.data.list || []
    }
  } catch (e) {
    console.error('获取最近记录失败', e)
  } finally {
    logsLoading.value = false
  }
}

const goRoute = (path) => {
  router.push(path)
}

onMounted(() => {
  getStat()
  // 只在事件列表为空时加载历史数据，避免页面切换重复添加
  if (eventList.length === 0) {
    getRecentLogs().then(() => {
      // API 返回倒序（最新在前），reverse 后按时间正序，再 unshift 保证最新在顶部
      recentLogs.value.reverse().forEach(log => {
        addDoorEvent({
          username: log.user_id ? log.username : '本地',
          device_name: log.device_name || '未知设备',
          location: log.device_location || '',
          action: log.action || '开门',
          timestamp: log.time
        })
      })
    })
  }
  timer = setInterval(() => {
    now.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style scoped>
.dashboard {
  padding: 4px;
}

.welcome-banner {
  margin-bottom: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fff;
}
.welcome-banner :deep(.el-card__body) {
  padding: 24px 28px;
}
.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.welcome-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.greeting-line {
  display: flex;
  align-items: center;
  gap: 6px;
}
.greeting-text {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}
.greeting-role {
  font-size: 13px;
  color: #909399;
  background: #f0f2f5;
  padding: 2px 10px;
  border-radius: 4px;
}
.welcome-sub {
  margin: 0;
  font-size: 14px;
  color: #909399;
}
.welcome-right {
  text-align: right;
}
.date-text {
  font-size: 14px;
  color: #606266;
}
.time-text {
  font-size: 32px;
  font-weight: 300;
  letter-spacing: 2px;
  color: #303133;
  font-variant-numeric: tabular-nums;
}

.stat-row {
  margin-bottom: 0;
}

.section-card {
  margin-top: 20px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.action-btn {
  height: 40px;
  padding: 0 20px;
  font-size: 14px;
  border-radius: 6px;
}

.ai-fab-wrap {
  position: fixed;
  right: 30px;
  bottom: 30px;
  z-index: 9999;
  cursor: pointer;
}
.ai-fab {
  width: 48px;
  height: 48px;
  border: 1px solid #dcdfe6;
  border-radius: 50%;
  background: #fff;
  color: #409eff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}
.ai-fab:hover {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

.section-card :deep(.el-table__empty-text) {
  color: #c0c4cc;
  font-size: 14px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.event-stream {
  max-height: 400px;
  overflow-y: auto;
}

.event-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}

.event-item:last-child {
  border-bottom: none;
}

.event-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
  background: #409eff;
}

.event-body {
  flex: 1;
  min-width: 0;
}

.event-main {
  font-size: 14px;
  color: #303133;
}

.event-user {
  font-weight: 600;
}

.event-sep {
  color: #909399;
  margin: 0 4px;
}

.event-device {
  font-weight: 500;
}

.event-location {
  color: #909399;
}

.event-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.event-time {
  font-size: 12px;
  color: #909399;
  font-variant-numeric: tabular-nums;
}

.event-empty {
  text-align: center;
  color: #c0c4cc;
  font-size: 14px;
  padding: 40px 0;
}

.event-slide-enter-active {
  transition: all 0.4s ease-out;
}

.event-slide-leave-active {
  transition: all 0.3s ease-in;
}

.event-slide-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.event-slide-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.event-slide-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
