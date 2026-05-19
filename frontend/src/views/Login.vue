<template>
  <div class="login-page">
    <div class="login-card">
      <!-- Logo 区域 -->
      <div class="header">
        <div class="icon-box">
          <el-icon class="lock-icon"><Lock /></el-icon>
        </div>
        <h1 class="title">智能门禁管理系统</h1>
        <p class="subtitle">智能识别 · 安全管控 · 高效管理</p>
      </div>

      <!-- 登录 / 注册 切换 -->
      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="系统登录" name="login">
          <el-form ref="loginFormRef" :model="form" :rules="loginRules" class="login-form" @submit.prevent="handleLogin">
            <el-form-item prop="username">
              <div class="input-wrap" :class="{ 'focus': focusedField === 'login-user' }">
                <el-icon class="input-icon"><User /></el-icon>
                <el-input
                  v-model="form.username"
                  placeholder="请输入用户名"
                  class="custom-input"
                  autocomplete="username"
                  @focus="focusedField = 'login-user'"
                  @blur="focusedField = ''"
                />
              </div>
            </el-form-item>

            <el-form-item prop="password">
              <div class="input-wrap" :class="{ 'focus': focusedField === 'login-pass' }">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  ref="loginPasswordRef"
                  v-model="form.password"
                  :type="loginPwdVisible ? 'text' : 'password'"
                  placeholder="请输入密码"
                  class="custom-input"
                  autocomplete="current-password"
                  @focus="focusedField = 'login-pass'"
                  @blur="focusedField = ''"
                  @keyup.enter="handleLogin"
                />
                <el-button text class="pwd-toggle" @click="loginPwdVisible = !loginPwdVisible">
                  <el-icon><View v-if="loginPwdVisible" /><Hide v-else /></el-icon>
                </el-button>
              </div>
            </el-form-item>

            <el-button
              type="primary"
              class="submit-btn"
              :loading="loginLoading"
              native-type="submit"
            >
              安全登录
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="账号注册" name="register">
          <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" class="login-form" @submit.prevent="handleRegister">
            <el-form-item prop="username">
              <div class="input-wrap" :class="{ 'focus': focusedField === 'reg-user' }">
                <el-icon class="input-icon"><User /></el-icon>
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入用户名"
                  class="custom-input"
                  autocomplete="username"
                  @focus="focusedField = 'reg-user'"
                  @blur="focusedField = ''"
                />
              </div>
            </el-form-item>

            <el-form-item prop="password">
              <div class="input-wrap" :class="{ 'focus': focusedField === 'reg-pass' }">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  v-model="registerForm.password"
                  :type="regPwdVisible ? 'text' : 'password'"
                  placeholder="密码至少 6 位"
                  class="custom-input"
                  autocomplete="new-password"
                  @focus="focusedField = 'reg-pass'"
                  @blur="focusedField = ''"
                />
                <el-button text class="pwd-toggle" @click="regPwdVisible = !regPwdVisible">
                  <el-icon><View v-if="regPwdVisible" /><Hide v-else /></el-icon>
                </el-button>
              </div>
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <div class="input-wrap" :class="{ 'focus': focusedField === 'reg-confirm' }">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  v-model="registerForm.confirmPassword"
                  :type="regConfirmVisible ? 'text' : 'password'"
                  placeholder="请再次输入密码"
                  class="custom-input"
                  autocomplete="new-password"
                  @focus="focusedField = 'reg-confirm'"
                  @blur="focusedField = ''"
                />
                <el-button text class="pwd-toggle" @click="regConfirmVisible = !regConfirmVisible">
                  <el-icon><View v-if="regConfirmVisible" /><Hide v-else /></el-icon>
                </el-button>
              </div>
            </el-form-item>

            <el-button
              type="primary"
              class="submit-btn"
              :loading="registerLoading"
              native-type="submit"
            >
              立即注册
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <!-- 底部版本 -->
      <div class="footer">v2.0 · 智能门禁管理系统</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, View, Hide } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const activeTab = ref('login')
const focusedField = ref('')
const loginLoading = ref(false)
const registerLoading = ref(false)
const loginPwdVisible = ref(false)
const regPwdVisible = ref(false)
const regConfirmVisible = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)

const form = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '', confirmPassword: '' })

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const validateConfirm = (rule, value, callback) => {
  if (!value) callback(new Error('请再次输入密码'))
  else if (value !== registerForm.value.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}


const handleLogin = async () => {
  if (!loginFormRef.value) return
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return
  loginLoading.value = true
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
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || '用户名或密码错误')
  } finally {
    loginLoading.value = false
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return
  registerLoading.value = true
  try {
    const res = await request.post('/auth/register', registerForm.value)
    if (res.code === 200) {
      ElMessage.success('注册成功，请登录')
      registerForm.value = { username: '', password: '', confirmPassword: '' }
      activeTab.value = 'login'
    } else {
      ElMessage.error(res.msg || '注册失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || '注册失败')
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f0f2f5;
}

/* ======== 登录卡片 ======== */
.login-card {
  width: 400px;
  padding: 40px 36px 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* ======== Logo 区域 ======== */
.header {
  text-align: center;
  margin-bottom: 28px;
}

.icon-box {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  background: #409eff;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lock-icon {
  font-size: 22px;
  color: #fff;
}

.title {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

/* ======== 标签页 ======== */
.login-tabs :deep(.el-tabs__header) {
  margin-bottom: 22px;
}

.login-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 500;
  height: 40px;
  line-height: 40px;
}

/* ======== 表单 ======== */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-form .el-form-item {
  margin-bottom: 0;
  width: 100%;
}

.input-wrap {
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: #c0c4cc;
  z-index: 1;
}

.custom-input { width: 100%; }

.custom-input :deep(.el-input__wrapper) {
  padding-left: 44px;
  padding-right: 40px;
  height: 44px;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}

.custom-input :deep(.el-input__inner) {
  font-size: 14px;
}

.pwd-toggle {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
  font-size: 16px;
  border: none;
  padding: 4px;
  color: #c0c4cc;
}

.pwd-toggle:hover {
  background: transparent;
  color: #909399;
}

/* ======== 提交按钮 ======== */
.submit-btn {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  margin-top: 4px;
}

.submit-btn :deep(.el-loading-spinner) .path {
  stroke: #fff;
}

/* ======== 底部 ======== */
.footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 14px;
  border-top: 1px solid #f0f2f5;
  font-size: 12px;
  color: #c0c4cc;
}
</style>
