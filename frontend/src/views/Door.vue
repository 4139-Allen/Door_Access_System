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

      <LogFilter
        :filter-form="filterForm"
        @search="resetPageAndSearch"
        @reset="resetFilter"
      />

      <LogTable
        :log-list="myLogs"
        :total="total"
        :loading="logsLoading"
        :show-user="role === 'admin'"
        empty-text="暂无开门记录"
        v-model:page="page"
        v-model:size="size"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useListFetch } from '@/composables/useListFetch'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import DoorDeviceSelect from '@/components/Door/DoorDeviceSelect.vue'
import LogFilter from '@/components/common/LogFilter.vue'
import LogTable from '@/components/common/LogTable.vue'

const deviceList = ref([])
const selectedDeviceId = ref(null)
const deviceLoading = ref(false)
const doorLoading = ref(false)
const role = ref(localStorage.getItem('role') || '')

const {
  dataList: myLogs, page, size, total,
  loading: logsLoading, filterForm,
  fetchData: getMyLogs, resetPageAndSearch, resetFilter
} = useListFetch('/door-logs', {
  defaultFilter: { device_name: '', status: '', time_range: [] },
  paramsBuilder: (f) => {
    const p = {}
    if (f.device_name?.trim()) p.device_name = f.device_name.trim()
    if (f.status?.trim()) p.status = f.status.trim()
    if (f.time_range?.length === 2) {
      p.start_time = f.time_range[0]
      p.end_time = f.time_range[1]
    }
    return p
  }
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
    ElMessage.success(res.msg || '开门成功')
    getMyLogs()
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '开门失败')
  } finally {
    setTimeout(() => { doorLoading.value = false }, 300)
  }
}

onMounted(() => {
  getMyDevices()
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
