<template>
  <BaseTable
    :data="userList" :loading="loading" :page="page" :size="size" :total="total"
    empty-text="暂无用户数据"
    @update:page="emit('update:page', $event)"
    @update:size="emit('update:size', $event)"
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
  </BaseTable>
</template>

<script setup>
import BaseTable from '@/components/common/BaseTable.vue'

defineProps({
  userList: Array,
  total: Number,
  page: Number,
  size: Number,
  loading: Boolean,
})
const emit = defineEmits(['update:page', 'update:size', 'show-devices', 'delete'])
</script>

<style>
@import '@/styles/page.css';
</style>

<style scoped>
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
</style>
