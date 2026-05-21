<template>
  <BaseTable
    :data="deviceList" :loading="loading" :page="page" :size="size" :total="total"
    empty-text="暂无设备数据"
    @update:page="emit('update:page', $event)"
    @update:size="emit('update:size', $event)"
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
  </BaseTable>
</template>

<script setup>
import BaseTable from '@/components/common/BaseTable.vue'

defineProps({
  deviceList: Array,
  total: Number,
  page: Number,
  size: Number,
  loading: Boolean,
})
const emit = defineEmits(['update:page', 'update:size', 'edit', 'delete'])
</script>

<style>
@import '@/styles/page.css';
</style>

<style scoped>
.location-text {
  font-size: 13px;
  color: #64748b;
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
</style>
