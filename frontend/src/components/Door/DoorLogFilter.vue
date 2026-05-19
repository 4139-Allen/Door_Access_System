<template>
  <div class="filter-bar">
    <div class="filter-row">
      <div class="filter-item">
        <el-input
          v-model="filterForm.device_name"
          placeholder="设备名称"
          style="width: 160px"
          clearable
          size="default"
        />
      </div>
      <div class="filter-item">
        <el-select
          v-model="filterForm.status"
          placeholder="状态"
          style="width: 130px"
          clearable
          size="default"
        >
          <el-option label="全部" value="" />
          <el-option label="成功" value="成功" />
          <el-option label="失败" value="失败" />
        </el-select>
      </div>
      <div class="filter-item">
        <el-date-picker
          v-model="filterForm.time_range"
          type="daterange"
          range-separator="~"
          start-placeholder="开始"
          end-placeholder="结束"
          style="width: 260px"
          value-format="YYYY-MM-DD HH:mm:ss"
          size="default"
        />
      </div>
      <div class="filter-actions">
        <el-button type="primary" @click="$emit('search')">搜索</el-button>
        <el-button @click="$emit('reset')">重置</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  filterForm: { type: Object, required: true }
})
const emit = defineEmits(['search', 'reset'])
</script>

<style scoped>
.filter-bar {
  padding: 16px;
  background: #f7f8fa;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  margin-bottom: 16px;
}
.filter-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}
.filter-item {
  display: flex;
  align-items: center;
}
.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}
.filter-actions .el-button {
  border-radius: 8px;
  display: flex;
  align-items: center;
}
</style>
