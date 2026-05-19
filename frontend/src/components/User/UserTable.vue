<template>
  <div class="table-wrapper">
    <el-table
      :data="userList"
      v-loading="loading"
      stripe
      empty-text="暂无用户数据"
      class="custom-table"
    >
      <el-table-column label="ID" prop="id" width="70" align="center" />
      <el-table-column label="用户名" prop="username" min-width="140">
        <template #default="{ row }">
          <div class="username-cell">
            <span class="avatar-placeholder">{{ row.username?.charAt(0)?.toUpperCase() }}</span>
            <span>{{ row.username }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="角色" width="100" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.role === 'admin' ? 'danger' : 'primary'"
            size="small"
            effect="light"
          >
            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" prop="created_at" width="175" />
      <el-table-column label="操作" width="230" align="center">
        <template #default="scope">
          <el-button
            size="small"
            class="action-btn-device"
            @click="$emit('show-devices', scope.row.id)"
          >
            设备
          </el-button>
          <el-button
            size="small"
            class="action-btn-delete"
            @click="$emit('delete', scope.row.id)"
          >
            删除
          </el-button>
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
  userList: Array,
  total: Number,
  page: Number,
  size: Number,
  loading: Boolean,
})

const emit = defineEmits(['update:page', 'update:size', 'show-devices', 'delete'])

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

.username-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar-placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #6366f1;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  border-radius: 6px;
  flex-shrink: 0;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #f1f5f9;
}

.action-btn-device {
  border: 1px solid #e2e8f0;
  color: #475569;
  background: #fff;
  border-radius: 8px;
  transition: all 0.2s;
}
.action-btn-device:hover {
  border-color: #6366f1;
  color: #6366f1;
  background: #f5f3ff;
  transform: translateY(-1px);
}

.action-btn-delete {
  border: 1px solid #fecaca;
  color: #ef4444;
  background: #fff;
  border-radius: 8px;
  transition: all 0.2s;
}
.action-btn-delete:hover {
  border-color: #ef4444;
  color: #fff;
  background: #ef4444;
  transform: translateY(-1px);
}
</style>
