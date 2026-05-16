<template>
  <div style="padding: 30px">
    <h1>欢迎进入门禁管理系统</h1>
    <el-row :gutter="20" style="margin-top: 30px">
      <el-col :span="6" v-if="role === 'admin'">
        <el-card shadow="hover">
          <h3>用户总数</h3>
          <p style="font-size: 24px;color:#409eff">{{ stat.user_total }}</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <h3>{{ role === 'admin' ? '设备总数' : '我的设备数' }}</h3>
          <p style="font-size: 24px;color:#67c23a">{{ stat.device_total }}</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <h3>{{ role === 'admin' ? '今日开门记录' : '我的今日开门记录' }}</h3>
          <p style="font-size: 24px;color:#e6a23c">{{ stat.today_log }}</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI 悬浮按钮 -->
    <el-button
      type="primary"
      circle
      style="position: fixed; right: 30px; bottom: 30px; z-index: 9999; width:50px; height:50px; font-size:18px"
      @click="aiDialog = true"
    >
      AI
    </el-button>

    <!-- AI 弹窗 -->
    <el-dialog v-model="aiDialog" title="💬 AI 智能门禁助手" width="500px">
      <div class="chat-box" ref="chatBox">
        <div v-for="(item, index) in msgList" :key="index" class="msg-wrap">
          <!-- AI消息：居左，头像在左，气泡在右 -->
          <div v-if="item.role === 'ai'" class="ai-row">
            <div class="avatar ai-avatar">🤖</div>
            <div class="bubble ai-bubble">{{ item.content }}</div>
          </div>
          <!-- 用户消息：居右，头像在右，气泡在左 -->
          <div v-else class="user-row">
            <div class="bubble user-bubble">{{ item.content }}</div>
            <div class="avatar user-avatar">👤</div>
          </div>
        </div>
      </div>

      <div style="margin-top:10px">
        <el-input
          v-model="userMsg"
          placeholder="请输入指令，例如：打开一楼大门"
          @keyup.enter="sendMessage"
          clearable
        >
          <template #append>
            <el-button type="primary" @click="sendMessage">发送</el-button>
          </template>
        </el-input>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import request from '@/utils/request'

const stat = ref({ user_total: 0, device_total: 0, today_log: 0 })
const role = ref(localStorage.getItem('role') || '')

const getStat = async () => {
  try {
    const res = await request.get('/statistics')
    if (res.code === 200) stat.value = res.data
  } catch (e) {
    console.error('获取统计失败', e)
  }
}

onMounted(() => { getStat() })

const aiDialog = ref(false)
const msgList = ref([])
const userMsg = ref('')
const chatBox = ref(null)

// 自动滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!userMsg.value) return
  const msg = userMsg.value
  userMsg.value = ''

  msgList.value.push({ role: 'user', content: msg })
  scrollToBottom()

  try {
    const res = await request.post('/ai/chat', { message: msg }, { timeout: 15000 })
    msgList.value.push({
      role: 'ai',
      content: res.data?.reply || 'AI 收到了'
    })
    scrollToBottom()
  } catch (err) {
    msgList.value.push({
      role: 'ai',
      content: '⚠️ AI 服务异常，请重试'
    })
    scrollToBottom()
  }
}
</script>

<style scoped>
.chat-box {
  height: 400px;
  overflow-y: auto;
  padding: 12px 16px;
  background: #fafbfc;
  border-radius: 8px;
}

/* 单条消息容器 */
.msg-wrap {
  margin-bottom: 16px;
  width: 100%;
  display: flex;
}

/* AI 左侧布局：头像 + 气泡 */
.ai-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  justify-content: flex-start;
  width: 100%;
}

/* 用户 右侧布局：气泡 + 头像 */
.user-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  justify-content: flex-end;
  width: 100%;
}

/* 头像通用样式 */
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.ai-avatar {
  background: #e5e6eb;
}
.user-avatar {
  background: #409eff;
  color: #fff;
}

/* 气泡样式 */
.bubble {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 12px;
  line-height: 1.5;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.ai-bubble {
  background: #ffffff;
  color: #333;
  border: 1px solid #eee;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.user-bubble {
  background: #409eff;
  color: #fff;
  border-bottom-right-radius: 4px;
}

/* 滚动条美化 */
.chat-box::-webkit-scrollbar {
  width: 4px;
}
.chat-box::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 4px;
}
</style>