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
        <el-button class="action-btn" @click="goRoute('/admin/door')">快速开门</el-button>
        <el-button class="action-btn" @click="goRoute('/admin/device')">设备管理</el-button>
        <el-button class="action-btn" @click="goRoute('/admin/log')">查看日志</el-button>
        <el-button v-if="role === 'admin'" class="action-btn" @click="goRoute('/admin/user')">用户管理</el-button>
      </div>
    </el-card>

    <!-- 最近开门记录 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <span class="section-title">最近开门记录</span>
      </template>
      <el-table
        v-loading="logsLoading"
        :data="recentLogs"
        stripe
        empty-text="暂无开门记录"
        style="width: 100%"
      >
        <el-table-column label="时间" prop="time" min-width="160" />
        <el-table-column label="设备" prop="device_name" min-width="100" />
        <el-table-column label="位置" prop="device_location" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" prop="action" width="80" />
        <el-table-column label="状态" prop="status" width="140">
          <template #default="{ row }">
            <el-tag
              :type="row.status === '成功' ? 'success' : 'danger'"
              effect="plain"
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- AI 悬浮按钮 -->
    <div class="ai-fab-wrap" @click="aiDialog = true">
      <button class="ai-fab">AI</button>
    </div>

    <AiChatBox v-model:visible="aiDialog" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import StatCard from '@/components/Dashboard/StatCard.vue'
import AiChatBox from '@/components/Dashboard/AiChatBox.vue'

const router = useRouter()
const role = ref(localStorage.getItem('role') || '')
const aiDialog = ref(false)
const logsLoading = ref(false)

const stat = ref({ user_total: 0, device_total: 0, today_log: 0 })
const recentLogs = ref([])

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
  getRecentLogs()
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
</style>
