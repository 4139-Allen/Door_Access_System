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
      <LogFilter
        :filter-form="filterForm"
        show-user
        show-labels
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

      <LogTable
        :log-list="logList"
        :total="total"
        :loading="loading"
        show-id
        avatar-color="#d97706"
        :page-sizes="[10, 20, 50, 100]"
        v-model:page="page"
        v-model:size="size"
      />
    </div>
  </div>
</template>

<script setup>
import { useListFetch } from '@/composables/useListFetch'
import LogFilter from '@/components/common/LogFilter.vue'
import LogTable from '@/components/common/LogTable.vue'

const {
  dataList: logList, page, size, total, loading, filterForm,
  fetchData: getLogList, resetPageAndSearch, resetFilter
} = useListFetch('/door-logs', {
  defaultFilter: { user_id: '', device_name: '', status: '', time_range: [] },
  paramsBuilder: (f) => {
    const p = {}
    if (f.user_id?.trim()) p.user_id = f.user_id.trim()
    if (f.device_name?.trim()) p.device_name = f.device_name.trim()
    if (f.status?.trim()) p.status = f.status.trim()
    if (f.time_range?.length === 2) {
      p.start_time = f.time_range[0]
      p.end_time = f.time_range[1]
    }
    return p
  }
})
</script>

<style>
@import '@/styles/page.css';
</style>

<style scoped>
.log-page {
  padding: 4px;
}
</style>
