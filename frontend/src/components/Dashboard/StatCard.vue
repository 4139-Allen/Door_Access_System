<template>
  <el-col :xs="24" :sm="12" :md="8" :lg="6">
    <el-card shadow="never" class="stat-card">
      <div class="stat-body">
        <div class="stat-info">
          <div class="stat-title">{{ title }}</div>
          <div class="stat-number" :style="{ color }">{{ number }}</div>
        </div>
      </div>
    </el-card>
  </el-col>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  number: { type: [Number, String], default: 0 },
  color: { type: String, default: '#409eff' },
})
</script>

<style scoped>
.stat-card {
  margin-bottom: 20px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.stat-body {
  padding: 4px 0;
}

.stat-info {
  min-width: 0;
}

.stat-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}
</style>
