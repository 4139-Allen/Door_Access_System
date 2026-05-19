<template>
  <div class="table-wrapper">
    <el-table
      :data="deviceList"
      v-loading="loading"
      stripe
      empty-text="暂无设备数据"
      class="custom-table"
    >
      <el-table-column label="ID" prop="id" width="70" align="center" />
      <el-table-column label="设备名称" prop="name" min-width="140">
        <template #default="{ row }">
          <span>{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="位置" prop="location" min-width="160">
        <template #default="{ row }">
          <span class="location-text">{{ row.location }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.status === 'online' ? 'success' : 'info'"
            size="small"
            effect="light"
          >
            <span class="status-dot" :class="row.status"></span>
            {{ row.status === 'online' ? '在线' : '离线' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" prop="created_at" width="175" />
      <el-table-column label="操作" width="200" align="center">
        <template #default="scope">
          <el-button
            size="small"
            class="action-btn-edit"
            @click="$emit('edit', scope.row)"
          >
            编辑
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
  deviceList: Array,
  total: Number,
  page: Number,
  size: Number,
  loading: Boolean,
})

const emit = defineEmits(['update:page', 'update:size', 'edit', 'delete'])

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


.location-text {
  font-size: 13px;
  color: #64748b;
}

.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 4px;
}
.status-dot.online {
  background: #22c55e;
}
.status-dot.offline {
  background: #94a3b8;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #f1f5f9;
}

.action-btn-edit {
  border: 1px solid #e2e8f0;
  color: #475569;
  background: #fff;
  border-radius: 8px;
  transition: all 0.2s;
}
.action-btn-edit:hover {
  border-color: #14b8a6;
  color: #14b8a6;
  background: #f0fdfa;
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
