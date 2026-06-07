<template>
  <div class="user-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <div>
          <h2 class="header-title">用户管理</h2>
          <p class="header-desc">管理系统用户账户与设备绑定关系</p>
        </div>
      </div>
      <div class="header-right">
        <span class="total-count">共 {{ total }} 位用户</span>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar-card">
      <div class="toolbar-section">
        <div class="section-label">搜索</div>
        <SearchFilter
          :filter-form="filterForm"
          field="username"
          placeholder="用户名"
          @search="resetPageAndSearch"
          @reset="resetFilter"
        />
      </div>

      <div class="toolbar-divider"></div>

      <div class="toolbar-section">
        <div class="section-label">新增用户</div>
        <AddForm :loading="adding" @add="addUser">
          <el-input
            v-model="addForm.username"
            placeholder="用户名"
            style="width: 140px"
            clearable
          />
          <el-input
            v-model="addForm.password"
            type="password"
            placeholder="密码 (至少6位)"
            style="width: 170px"
            show-password
          />
        </AddForm>
      </div>

      <div class="toolbar-divider"></div>

      <div class="toolbar-section">
        <div class="section-label">设备绑定</div>
        <UserBindForm
          :bind-form="bindForm"
          :bind-loading="binding"
          :unbind-loading="unbinding"
          @bind="bindDevice"
          @unbind="unbindDevice"
        />
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="table-card">
      <div class="table-header">
        <span class="table-header-title">用户列表</span>
        <el-tag size="small" type="info" effect="plain">
          共 {{ total }} 条记录
        </el-tag>
      </div>

      <UserTable
        :user-list="userList"
        :total="total"
        :loading="loading"
        v-model:page="page"
        v-model:size="size"
        @show-devices="showDevices"
        @delete="deleteUser"
      />
    </div>

    <!-- 绑定设备弹窗 -->
    <el-dialog v-model="deviceDialogVisible" width="min(420px, 90vw)" top="30vh">
      <template #header>
        <span>绑定设备</span>
      </template>

      <div v-if="deviceList.length === 0" class="empty-devices">
        <p>该用户未绑定任何设备</p>
      </div>
      <div v-else class="device-grid">
        <div
          v-for="d in deviceList"
          :key="d"
          class="device-chip"
        >
          <span>设备 #{{ d }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useListFetch } from '@/composables/useListFetch'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import SearchFilter from '@/components/common/SearchFilter.vue'
import AddForm from '@/components/common/AddForm.vue'
import UserBindForm from '@/components/User/UserBindForm.vue'
import UserTable from '@/components/User/UserTable.vue'

const {
  dataList: userList, page, size, total, loading, filterForm,
  fetchData: getUserList, resetPageAndSearch, resetFilter
} = useListFetch('/users', {
  defaultFilter: { username: '' },
  paramsBuilder: (f) => f.username?.trim() ? { username: f.username.trim() } : {}
})

const addForm = ref({ username: '', password: '' })
const bindForm = ref({ user_id: '', device_id: '' })
const adding = ref(false)
const binding = ref(false)
const unbinding = ref(false)
const deviceDialogVisible = ref(false)
const deviceList = ref([])

const addUser = async () => {
  if (!addForm.value.username || !addForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  adding.value = true
  try {
    const res = await request.post('/users', addForm.value)
    if (res.code === 200) {
      ElMessage.success('新增成功')
      getUserList()
      addForm.value = { username: '', password: '' }
    } else {
      ElMessage.error(res.msg || '新增失败')
    }
  } catch (e) {
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    adding.value = false
  }
}

const deleteUser = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？此操作不可撤销。', '确认删除', {
      type: 'warning',
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    })
    await request.delete(`/users/${id}`)
    ElMessage.success('删除成功')
    getUserList()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const showDevices = async (uid) => {
  try {
    const res = await request.get(`/users/${uid}/devices`)
    deviceList.value = [...new Set(res.data || [])]
    deviceDialogVisible.value = true
  } catch (e) {
    ElMessage.error('获取失败')
  }
}

const bindDevice = async () => {
  if (!bindForm.value.user_id || !bindForm.value.device_id) {
    ElMessage.warning('请输入用户ID和设备ID')
    return
  }
  binding.value = true
  try {
    await request.post(`/devices/${bindForm.value.device_id}/bind`, {
      user_id: bindForm.value.user_id
    })
    ElMessage.success('绑定成功')
    bindForm.value = { user_id: '', device_id: '' }
  } catch (e) {
    ElMessage.error('绑定失败')
  } finally {
    binding.value = false
  }
}

const unbindDevice = async () => {
  if (!bindForm.value.user_id || !bindForm.value.device_id) {
    ElMessage.warning('请输入用户ID和设备ID')
    return
  }
  unbinding.value = true
  try {
    await ElMessageBox.confirm('确定要解绑设备吗？', '确认解绑', {
      type: 'warning',
      confirmButtonText: '确定解绑',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    })
    await request.delete(`/devices/${bindForm.value.device_id}/unbind`, {
      params: { user_id: bindForm.value.user_id }
    })
    ElMessage.success('解绑成功')
    bindForm.value = { user_id: '', device_id: '' }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('解绑失败')
    }
  } finally {
    unbinding.value = false
  }
}
</script>

<style>
@import '@/styles/page.css';
</style>

<style scoped>
.user-page {
  padding: 4px;
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

.empty-devices {
  text-align: center;
  padding: 32px 0;
  color: #909399;
}

.empty-devices p {
  margin: 0;
  font-size: 14px;
}

.device-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.device-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 13px;
  color: #606266;
}
</style>
