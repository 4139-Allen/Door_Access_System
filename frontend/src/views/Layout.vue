<template>
  <el-container style="height: 100vh;">
    <el-aside width="200px" style="background-color: #2f4050;">
      <div style="height:60px;line-height:60px;text-align:center;color:#fff;font-size:18px;border-bottom:1px solid #333;">
        智能门禁管理系统
      </div>
      <el-menu
        background-color="#2f4050"
        text-color="#fff"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/admin/dashboard">首页</el-menu-item>
        <el-menu-item index="/admin/door">用户开门</el-menu-item>
        <el-menu-item index="/admin/user" v-if="role === 'admin'">用户管理</el-menu-item>
        <el-menu-item index="/admin/device" v-if="role === 'admin'">设备管理</el-menu-item>
        <el-menu-item index="/admin/log" v-if="role === 'admin'">门禁日志</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header style="background:#fff;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center;padding:0 20px;">
        <span>欢迎{{ role === 'admin' ? '管理员' : '普通用户' }}</span>
        <div style="display: flex; gap: 10px; align-items: center;">
          <el-button type="primary" link @click="showPasswordDialog = true">
            <el-icon><Lock /></el-icon>
            修改密码
          </el-button>
          <el-button text @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main style="background:#f5f7fa;padding:20px;">
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>

  <!-- 修改密码对话框 -->
  <el-dialog
    v-model="showPasswordDialog"
    title="修改密码"
    width="450px"
    :close-on-click-modal="false"
  >
    <el-form
      ref="passwordFormRef"
      :model="passwordForm"
      :rules="passwordRules"
      label-width="100px"
    >
      <el-form-item label="原密码" prop="old_password">
        <el-input
          v-model="passwordForm.old_password"
          type="password"
          placeholder="请输入原密码"
          show-password
        />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input
          v-model="passwordForm.new_password"
          type="password"
          placeholder="请输入新密码（6-72个字符）"
          show-password
        />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirm_password">
        <el-input
          v-model="passwordForm.confirm_password"
          type="password"
          placeholder="请再次输入新密码"
          show-password
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showPasswordDialog = false">取消</el-button>
      <el-button type="primary" @click="handleChangePassword" :loading="changing">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ref, reactive } from 'vue'
import { Lock } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const role = ref(localStorage.getItem('role') || '')

// 修改密码相关
const showPasswordDialog = ref(false)
const passwordFormRef = ref(null)
const changing = ref(false)

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 验证确认密码
const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' },
    { min: 6, max: 72, message: '密码长度为6-72个字符', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 72, message: '密码长度为6-72个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
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
        // 清空表单
        passwordForm.old_password = ''
        passwordForm.new_password = ''
        passwordForm.confirm_password = ''
        // 退出登录
        setTimeout(() => {
          logout()
        }, 1500)
      } else {
        ElMessage.error(res.msg || '密码修改失败')
      }
    } catch (error) {
      console.error('修改密码错误:', error)
      ElMessage.error(error.response?.data?.msg || '密码修改失败')
    } finally {
      changing.value = false
    }
  })
}

const logout = async () => {
  try {
    await request.post('/auth/logout')
  } catch (e) {
    console.log('退出请求失败', e)
  } finally {
    localStorage.clear()
    ElMessage.success('已退出')
    router.push('/login')
  }
}
</script>

<style scoped>
:deep(.el-menu-item.is-active) {
  background-color: #1f2d3d !important;
  border-left: 4px solid #409eff;
  color: #fff !important;
}
</style>
