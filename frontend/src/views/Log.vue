<template>
  <div class="log-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <div>
          <h2 class="header-title">门禁日志</h2>
          <p class="header-desc">查看所有门禁开关记录与操作历史</p>
        </div>
      </div>
      <div class="header-right">
        <span class="total-count">共 {{ total }} 条记录</span>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="filter-card">
      <AllLogFilter
        :filter-form="filterForm"
        @search="resetPageAndSearch"
        @reset="resetFilter"
      />
    </div>

    <!-- 列表 -->
    <div class="table-card">
      <div class="table-header">
        <span class="table-header-title">开门记录</span>
        <el-tag size="small" type="info" effect="plain">
          共 {{ total }} 条记录
        </el-tag>
      </div>

      <AllLogTable
        :log-list="logList"
        :total="total"
        :loading="loading"
        v-model:page="page"
        v-model:size="size"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import request from '@/utils/request'
import AllLogFilter from '@/components/Log/AllLogFilter.vue'
import AllLogTable from '@/components/Log/AllLogTable.vue'

const logList = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const loading = ref(false)

const filterForm = ref({
  user_id: '',
  device_name: '',
  status: '',
  time_range: []
})

watch([page, size], () => {
  getLogList()
})

const getLogList = async () => {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value }
    if (filterForm.value.user_id?.trim()) params.user_id = filterForm.value.user_id.trim()
    if (filterForm.value.device_name?.trim()) params.device_name = filterForm.value.device_name.trim()
    if (filterForm.value.status?.trim()) params.status = filterForm.value.status.trim()
    if (filterForm.value.time_range?.length === 2) {
      params.start_time = filterForm.value.time_range[0]
      params.end_time = filterForm.value.time_range[1]
    }
    const res = await request.get('/door-logs', { params })
    logList.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetPageAndSearch = () => {
  page.value = 1
  getLogList()
}

const resetFilter = () => {
  filterForm.value = { user_id: '', device_name: '', status: '', time_range: [] }
  page.value = 1
  getLogList()
}

onMounted(() => getLogList())
</script>

<style scoped>
.log-page {
  padding: 4px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px 24px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-desc {
  margin: 4px 0 0;
  font-size: 13px;
  color: #909399;
}

.total-count {
  font-size: 14px;
  color: #606266;
}

.filter-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 20px;
}

.table-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid #ebeef5;
}

.table-header-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
