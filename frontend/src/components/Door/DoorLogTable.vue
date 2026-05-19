<template>
  <div class="table-wrapper">
    <el-table
      :data="logList"
      v-loading="loading"
      stripe
      empty-text="暂无开门记录"
      class="custom-table"
    >
      <el-table-column label="时间" prop="time" min-width="170">
        <template #default="{ row }">
          <span class="time-text">{{ row.time }}</span>
        </template>
      </el-table-column>
      <el-table-column v-if="role === 'admin'" label="用户" width="160">
        <template #default="{ row }">
          <div class="user-cell">
            <span class="user-avatar">{{ (row.username || '?').charAt(0) }}</span>
            <div class="user-info">
              <span class="user-name">{{ row.username || '未知' }}</span>
              <span class="user-id">ID: {{ row.user_id }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="设备" min-width="120">
        <template #default="{ row }">
          <span class="device-text">{{ row.device_name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="位置" prop="device_location" min-width="110" show-overflow-tooltip />
      <el-table-column label="操作" prop="action" width="70" align="center">
        <template #default="{ row }">
          <el-tag :type="row.action === '开门' ? 'primary' : 'warning'" size="small" effect="plain">
            {{ row.action }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" min-width="160" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.status === '成功' ? 'success' : 'danger'"
            size="small"
            effect="light"
          >
            <span class="status-dot" :class="row.status === '成功' ? 'success' : 'fail'"></span>
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrap">
      <el-pagination
        :current-page="page"
        :page-size="size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="emitPage('page', $event)"
        @size-change="emitPage('size', $event)"
      />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  logList: Array,
  total: Number,
  page: Number,
  size: Number,
  loading: Boolean,
  role: String,
})

const emit = defineEmits(['update:page', 'update:size'])

const emitPage = (field, val) => {
  if (field === 'page') emit('update:page', val)
  if (field === 'size') emit('update:size', val)
}
</script>

<style scoped>
.table-wrapper {
  padding: 0;
}
.custom-table {
  width: 100%;
  --el-table-border-color: #f1f5f9;
  --el-table-header-bg-color: #f8fafc;
}
.custom-table :deep(th.el-table__cell) {
  font-weight: 600;
  color: #475569;
  background-color: #f8fafc;
  font-size: 13px;
}
.custom-table :deep(.el-table__row) {
  transition: background-color 0.2s;
}
.custom-table :deep(.el-table__row:hover) {
  background-color: #f1f5f9 !important;
}
.custom-table :deep(.el-table__empty-text) {
  color: #94a3b8;
  font-size: 14px;
}

.time-text {
  font-size: 13px;
  color: #64748b;
  font-variant-numeric: tabular-nums;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: #6366f1;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.user-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
  line-height: 1.3;
}
.user-id {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.3;
}

.device-text {
  font-size: 13px;
}

.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 4px;
}
.status-dot.success {
  background: #22c55e;
}
.status-dot.fail {
  background: #ef4444;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #f1f5f9;
}
</style>
