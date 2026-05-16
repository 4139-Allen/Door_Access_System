<template>
  <el-card>
    <h2>{{ role === 'admin' ? '门禁开门' : '用户开门' }}</h2>
    <el-divider />

    <!-- 选择设备开门 -->
    <el-form :model="doorForm" inline style="margin-bottom:20px;">
      <el-form-item label="选择设备">
        <el-select
          v-model="selectedDeviceId"
          placeholder="请选择设备"
          style="width: 280px"
        >
          <el-option
            v-for="d in deviceList"
            :key="d.id"
            :label="`${d.name} | ${d.location}`"
            :value="d.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="openDoor">开门</el-button>
      </el-form-item>
    </el-form>

    <!-- 分割线 -->
    <el-divider style="margin: 15px 0;"></el-divider>

    <!-- 筛选区域 -->
    <el-form :model="filterForm" inline style="margin-bottom:20px;">
      <el-form-item label="设备名称">
        <el-input
          v-model="filterForm.device_name"
          placeholder="输入设备名称搜索"
          style="width: 220px"
          clearable
        />
      </el-form-item>

      <el-form-item label="操作状态">
        <el-select
          v-model="filterForm.status"
          placeholder="全部状态"
          style="width: 180px"
          clearable
        >
          <el-option label="成功" value="成功" />
          <el-option label="失败" value="失败" />
        </el-select>
      </el-form-item>

      <el-form-item label="操作时间">
        <el-date-picker
          v-model="filterForm.time_range"
          type="daterange"
          range-separator="~"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          style="width: 380px"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="resetPageAndSearch">搜索</el-button>
        <el-button @click="resetFilter" style="margin-left:10px">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 开门日志 -->
    <h3>{{ role === 'admin' ? '所有开门记录' : '我的开门记录' }}</h3>
    <el-table :data="myLogs" border stripe>
      <el-table-column v-if="role === 'admin'" label="用户ID" prop="user_id" width="100" />
      <el-table-column label="设备名称" prop="device_name" />
      <el-table-column label="设备位置" prop="device_location" />
      <el-table-column label="操作" prop="action" />
      <el-table-column label="状态" prop="status" />
      <el-table-column label="时间" prop="time" />
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="page"
      v-model:page-size="size"
      :total="total"
      layout="total, prev, pager, next, jumper"
      style="margin-top:20px; text-align:right"
      @current-change="getMyLogs"
      @size-change="getMyLogs"
      :locale="{
        prevText: '上一页',
        nextText: '下一页',
        total: '共 {total} 条',
        goto: '前往',
        pageClassifier: '页'
      }"
    />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const deviceList = ref([])
const myLogs = ref([])
const selectedDeviceId = ref(null)
const doorForm = ref({})

const page = ref(1)
const size = ref(10)
const total = ref(0)

// 获取用户角色
const role = ref(localStorage.getItem('role') || '')

const filterForm = ref({
  device_name: '',
  status: '',
  time_range: []
})

// ====================== 获取设备列表 ======================
const getMyDevices = async () => {
  try {
    const res = await request.get('/devices')
    // 后端已经做了权限控制：普通用户只返回自己绑定的，管理员返回全部
    deviceList.value = res.data.list
  } catch (e) {
    console.error('获取设备失败', e)
  }
}
// ======================================================================

const openDoor = async () => {
  if (!selectedDeviceId.value) {
    ElMessage.warning('请选择设备')
    return
  }

  try {
    await request.post(`/doors/${selectedDeviceId.value}/open`)
    ElMessage.success('开门成功')
    getMyLogs()
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '开门失败')
  }
}

const getMyLogs = async () => {
  try {
    const params = {
      page: page.value,
      size: size.value,
    }

    // 只在有值时才添加筛选参数
    if (filterForm.value.device_name && filterForm.value.device_name.trim() !== '') {
      params.device_name = filterForm.value.device_name.trim()
    }

    // 只有当 status 不为空时才添加（修复：空字符串不传）
    if (filterForm.value.status && filterForm.value.status.trim() !== '') {
      params.status = filterForm.value.status
    }

    if (filterForm.value.time_range && filterForm.value.time_range.length === 2) {
      params.start_time = filterForm.value.time_range[0]
      params.end_time = filterForm.value.time_range[1]
    }

    const res = await request.get('/door-logs', { params })
    myLogs.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error('获取日志失败', e)
    ElMessage.error('获取日志失败')
  }
}

const resetPageAndSearch = () => {
  page.value = 1
  getMyLogs()
}

const resetFilter = () => {
  filterForm.value = {
    device_name: '',
    status: '',
    time_range: []
  }
  page.value = 1
  getMyLogs()
}

onMounted(() => {
  getMyDevices()
  getMyLogs()
})
</script>
