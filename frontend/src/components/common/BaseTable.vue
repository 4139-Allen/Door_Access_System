<template>
  <div class="table-wrapper">
    <el-table
      v-bind="$attrs"
      class="custom-table"
      stripe
      v-loading="loading"
    >
      <slot />
    </el-table>
    <div class="pagination-wrap">
      <el-pagination
        :current-page="page"
        :page-size="size"
        :total="total"
        :page-sizes="pageSizes"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="emit('update:page', $event)"
        @size-change="emit('update:size', $event)"
      />
    </div>
  </div>
</template>

<script setup>
defineProps({
  loading: Boolean,
  page: Number,
  size: Number,
  total: Number,
  pageSizes: { type: Array, default: () => [10, 20, 50] },
})
const emit = defineEmits(['update:page', 'update:size'])
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
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #f1f5f9;
}
</style>
