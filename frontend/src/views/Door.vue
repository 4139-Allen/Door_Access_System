<template>
  <div class="door-page">
    <!-- 门禁控制 -->
    <el-card class="control-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">门禁控制</span>
          </div>
          <el-tag v-if="deviceList.length > 0" type="success" effect="plain" size="small">
            可用设备 {{ deviceList.length }} 台
          </el-tag>
        </div>
      </template>
      <DoorDeviceSelect
        :device-list="deviceList"
        :loading="deviceLoading"
        v-model:selected-id="selectedDeviceId"
        :opening="doorLoading"
        @open="openDoor"
      />
    </el-card>

    <!-- 开门记录 -->
    <el-card class="log-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">{{ role === 'admin' ? '所有开门记录' : '我的开门记录' }}</span>
          </div>
          <span v-if="total > 0" class="header-total">共 {{ total }} 条</span>
        </div>
      </template>

      <DoorLogFilter
        :filter-form="filterForm"
        @search="resetPageAndSearch"
        @reset="resetFilter"
      />

      <DoorLogTable
        :log-list="myLogs"
        :total="total"
        :loading="logsLoading"
        :role="role"
        v-model:page="page"
        v-model:size="size"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import DoorDeviceSelect from '@/components/Door/DoorDeviceSelect.vue'
import DoorLogFilter from '@/components/Door/DoorLogFilter.vue'
import DoorLogTable from '@/components/Door/DoorLogTable.vue'

const deviceList = ref([])
const myLogs = ref([])
const selectedDeviceId = ref(null)
const deviceLoading = ref(false)
const logsLoading = ref(false)
const doorLoading = ref(false)

const page = ref(1)
const size = ref(10)
const total = ref(0)
const role = ref(localStorage.getItem('role') || '')

const filterForm = ref({
  device_name: '',
  status: '',
  time_range: []
})

watch([page, size], () => {
  getMyLogs()
})

const getMyDevices = async () => {
  deviceLoading.value = true
  try {
    const res = await request.get('/devices')
    deviceList.value = res.data.list || []
  } catch (e) {
    console.error('获取设备失败', e)
  } finally {
    deviceLoading.value = false
  }
}

const openDoor = async () => {
  if (!selectedDeviceId.value) {
    ElMessage.warning('请选择设备')
    return
  }
  doorLoading.value = true
  try {
    const res = await request.post(`/doors/${selectedDeviceId.value}/open`)
    ElMessage.success(res.data?.msg || '开门成功')
    getMyLogs()
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '开门失败')
  } finally {
    setTimeout(() => { doorLoading.value = false }, 300)
  }
}

const getMyLogs = async () => {
  logsLoading.value = true
  try {
    const params = { page: page.value, size: size.value }
    if (filterForm.value.device_name?.trim()) params.device_name = filterForm.value.device_name.trim()
    if (filterForm.value.status?.trim()) params.status = filterForm.value.status.trim()
    if (filterForm.value.time_range?.length === 2) {
      params.start_time = filterForm.value.time_range[0]
      params.end_time = filterForm.value.time_range[1]
    }
    const res = await request.get('/door-logs', { params })
    myLogs.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error('获取日志失败', e)
  } finally {
    logsLoading.value = false
  }
}

const resetPageAndSearch = () => {
  page.value = 1
  getMyLogs()
}

const resetFilter = () => {
  filterForm.value = { device_name: '', status: '', time_range: [] }
  page.value = 1
  getMyLogs()
}

onMounted(() => {
  getMyDevices()
  getMyLogs()
})
</script>

<style scoped>
.door-page {
  padding: 4px;
}

.control-card,
.log-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}
.log-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.header-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
.header-total {
  font-size: 13px;
  color: #909399;
}
</style>
