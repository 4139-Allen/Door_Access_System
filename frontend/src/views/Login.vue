<template>
  <div class="login-page">
    <div class="login-card">
      <!-- 图标 + 标题 -->
      <div class="header">
        <div class="icon-box">
          <el-icon :size="40" color="#fff">
            <Lock />
          </el-icon>
        </div>
        <h1 class="title">欢迎回来</h1>
        <p class="subtitle">登录以继续访问门禁系统</p>
      </div>

      <!-- 标签页切换 -->
      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="form" class="login-form">
            <!-- 用户名 -->
            <div class="form-item">
              <label class="label">用户名</label>
              <div class="input-wrap">
                <el-icon class="input-icon"><User /></el-icon>
                <el-input
                  v-model="form.username"
                  placeholder="请输入用户名"
                  class="custom-input"
                />
              </div>
            </div>

            <!-- 密码 -->
            <div class="form-item">
              <label class="label">密码</label>
              <div class="input-wrap">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  v-model="form.password"
                  type="password"
                  placeholder="请输入密码"
                  class="custom-input"
                  @keyup.enter="handleLogin"
                />
              </div>
            </div>

            <!-- 登录按钮 -->
            <el-button
              type="primary"
              class="login-btn"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" class="login-form">
            <!-- 用户名 -->
            <div class="form-item">
              <label class="label">用户名</label>
              <div class="input-wrap">
                <el-icon class="input-icon"><User /></el-icon>
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入用户名"
                  class="custom-input"
                />
              </div>
            </div>

            <!-- 密码 -->
            <div class="form-item">
              <label class="label">密码</label>
              <div class="input-wrap">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码"
                  class="custom-input"
                />
              </div>
            </div>

            <!-- 确认密码 -->
            <div class="form-item">
              <label class="label">确认密码</label>
              <div class="input-wrap">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入密码"
                  class="custom-input"
                />
              </div>
            </div>

            <!-- 注册按钮 -->
            <el-button
              type="primary"
              class="register-btn"
              @click="handleRegister"
            >
              注 册
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const activeTab = ref('login')

const form = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  try {
    const res = await request.post('/auth/login', form.value)
    if (res.code === 200) {
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('role', res.data.role)
      ElMessage.success('登录成功')
      router.push('/admin/dashboard')
    } else {
      ElMessage.error(res.msg || '登录失败')
    }
  } catch {
    ElMessage.error('用户名或密码错误')
  }
}

const handleRegister = async () => {
  const { username, password, confirmPassword } = registerForm.value

  // 验证是否为空
  if (!username || !password || !confirmPassword) {
    ElMessage.warning('请填写所有字段')
    return
  }

  // 验证用户名长度
  if (username.length < 1) {
    ElMessage.error('用户名至少需要1个字符')
    return
  }

  if (username.length > 50) {
    ElMessage.error('用户名不能超过50个字符')
    return
  }

  // 验证用户名格式
  if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(username)) {
    ElMessage.error('用户名只能包含字母、数字、下划线和中文')
    return
  }

  // 验证密码长度
  if (password.length < 6) {
    ElMessage.error(`密码至少需要6个字符（当前${password.length}个）`)
    return
  }

  if (password.length > 72) {
    ElMessage.error('密码不能超过72个字符')
    return
  }

  // 验证两次密码是否一致
  if (password !== confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  try {
    const res = await request.post('/auth/register', {
      username: username,
      password: password
    })

    if (res.code === 200) {
      ElMessage.success('注册成功，请登录')
      // 清空注册表单并切换到登录标签
      registerForm.value = {
        username: '',
        password: '',
        confirmPassword: ''
      }
      activeTab.value = 'login'
    } else {
      ElMessage.error(res.msg || '注册失败')
    }
  } catch (error) {
    // 打印详细错误信息用于调试
    console.error('注册错误:', error)
    if (error.response) {
      console.error('错误响应:', error.response.data)
      // 处理 422 验证错误
      if (error.response.status === 422) {
        const detail = error.response.data.detail
        if (Array.isArray(detail)) {
          // FastAPI 验证错误格式
          const messages = detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join('; ')
          ElMessage.error(`数据验证失败: ${messages}`)
        } else {
          ElMessage.error('数据格式错误')
        }
        return
      }
    }
    ElMessage.error(error.response?.data?.msg || error.response?.data?.message || '注册失败')
  }
}
</script>

<style scoped>
/* 页面背景：浅色渐变 */
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f0f4ff 0%, #e6edff 100%);
}

/* 卡片容器 */
.login-card {
  width: 420px;
  padding: 50px 40px;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

/* 顶部图标+标题 */
.header {
  text-align: center;
  margin-bottom: 30px;
}

.icon-box {
  width: 72px;
  height: 72px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.title {
  margin: 0 0 10px;
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
}

.subtitle {
  margin: 0;
  font-size: 16px;
  color: #6b7280;
}

/* 标签页样式 */
.login-tabs {
  margin-top: 20px;
}

.login-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.login-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}

.login-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
}

.login-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
}

.login-tabs :deep(.el-tabs__active-bar) {
  background-color: #667eea;
}

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.label {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
}

.input-wrap {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 20px;
  color: #9ca3af;
  z-index: 1;
}

.custom-input {
  width: 100%;
}

.custom-input :deep(.el-input__wrapper) {
  padding-left: 48px;
  border-radius: 999px;
  height: 52px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  box-shadow: none;
}

.custom-input :deep(.el-input__wrapper:hover) {
  border-color: #667eea;
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 52px;
  border-radius: 999px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-size: 18px;
  font-weight: 500;
  margin-top: 8px;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

/* 注册按钮 */
.register-btn {
  width: 100%;
  height: 52px;
  border-radius: 999px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-size: 18px;
  font-weight: 500;
  margin-top: 8px;
  transition: all 0.3s ease;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}
</style>
