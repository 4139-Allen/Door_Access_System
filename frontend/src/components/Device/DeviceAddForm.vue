<template>
  <div class="add-form" @submit.prevent="$emit('add')">
    <el-input
      v-model="addForm.name"
      placeholder="设备名称"
      style="width: 150px"
      clearable
    />
    <el-input
      v-model="addForm.location"
      placeholder="设备位置"
      style="width: 170px"
      clearable
    />
    <el-button type="primary" native-type="submit" :loading="loading">新增</el-button>
  </div>
</template>

<script setup>
defineProps({ addForm: { type: Object, required: true }, loading: { type: Boolean, default: false } })
const emit = defineEmits(['add'])
</script>

<style scoped>
.add-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
</style>
