<template>
  <el-card>
    <h2>用户管理</h2>
    <el-divider />

    <!-- 筛选区：用户名搜索 + 加了 submit.prevent 阻止回车刷新 -->
    <el-form :model="filterForm" inline style="margin-bottom:20px;" @submit.prevent="resetPageAndSearch">
      <el-form-item label="用户名">
        <el-input
          v-model="filterForm.username"
          placeholder="搜索用户名"
          style="width: 280px"
          clearable
          @keydown.enter.exact="resetPageAndSearch"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="resetPageAndSearch">搜索</el-button>
        <el-button @click="resetFilter" style="margin-left: 10px">重置</el-button>
      </el-form-item>
    </el-form>

    <el-divider style="margin: 15px 0;"></el-divider>

    <!-- 新增用户区 -->
    <el-form :model="addForm" inline style="margin-bottom:20px;">
      <el-form-item label="用户名">
        <el-input v-model="addForm.username" style="width: 280px" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="addForm.password" type="password" style="width: 280px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="addUser">新增用户</el-button>
      </el-form-item>
    </el-form>

    <el-divider style="margin: 15px 0;"></el-divider>

    <!-- 绑定解绑区 -->
    <el-form :model="bindForm" inline style="margin-bottom:20px;">
      <el-form-item label="用户ID">
        <el-input v-model="bindForm.user_id" style="width: 280px" />
      </el-form-item>
      <el-form-item label="设备ID">
        <el-input v-model="bindForm.device_id" style="width: 280px" />
      </el-form-item>
      <el-form-item>
        <el-button type="success" @click="bindDevice">绑定设备</el-button>
        <el-button type="warning" @click="unbindDevice" style="margin-left: 10px">解绑设备</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="userList" border>
      <el-table-column label="ID" prop="id" />
      <el-table-column label="用户名" prop="username" />
      <el-table-column label="角色" prop="role" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button type="primary" size="small" @click="showDevices(scope.row.id)">查看绑定设备</el-button>
          <el-button type="danger" size="small" style="margin-left: 10px" @click="deleteUser(scope.row.id)">删除用户</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top:20px; text-align:right"
      v-model:current-page="page"
      v-model:page-size="size"
      :total="total"
      layout="total, prev, pager, next, jumper"
      @size-change="getUserList"
      @current-change="getUserList"
    />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const userList = ref([])
const addForm = ref({ username: '', password: '' })
const bindForm = ref({ user_id: '', device_id: '' })

const page = ref(1)
const size = ref(10)
const total = ref(0)

const filterForm = ref({
  username: ''
})

const getUserList = async () => {
  try {
    const res = await request.get('/users', {
      params: {
        page: page.value,
        size: size.value,
        username: filterForm.value.username
      }
    })

    userList.value = res.data.list
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  }
}

const resetPageAndSearch = () => {
  page.value = 1
  getUserList()
}

const resetFilter = () => {
  filterForm.value = {
    username: ''
  }
  page.value = 1
  getUserList()
}

const addUser = async () => {
  if (!addForm.value.username || !addForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
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
  }
}

const deleteUser = async (id) => {
  try {
    await request.delete(`/users/${id}`)
    ElMessage.success('删除成功')
    getUserList()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const showDevices = async (uid) => {
  try {
    const res = await request.get(`/users/${uid}/devices`)
    const deviceList = res.data || []
    const uniqueList = [...new Set(deviceList)]
    ElMessage.info('绑定设备ID：' + uniqueList.join('、'))
  } catch (e) {
    ElMessage.error('获取失败')
  }
}

const bindDevice = async () => {
  if (!bindForm.value.user_id || !bindForm.value.device_id) {
    ElMessage.warning('请输入用户ID和设备ID')
    return
  }
  try {
    await request.post(`/devices/${bindForm.value.device_id}/bind`, {
      user_id: bindForm.value.user_id
    })
    ElMessage.success('绑定成功')
    bindForm.value = { user_id: '', device_id: '' }
  } catch (e) {
    ElMessage.error('绑定失败')
  }
}

const unbindDevice = async () => {
  if (!bindForm.value.user_id || !bindForm.value.device_id) {
    ElMessage.warning('请输入用户ID和设备ID')
    return
  }
  try {
    await request.delete(`/devices/${bindForm.value.device_id}/unbind`, {
      params: {
        user_id: bindForm.value.user_id
      }
    })
    ElMessage.success('解绑成功')
    bindForm.value = { user_id: '', device_id: '' }
  } catch (e) {
    ElMessage.error('解绑失败')
  }
}

onMounted(() => {
  getUserList()
})
</script>