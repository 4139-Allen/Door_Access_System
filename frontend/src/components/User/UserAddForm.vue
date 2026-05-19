<template>
  <div class="add-form" @submit.prevent="$emit('add')">
    <el-input
      v-model="addForm.username"
      placeholder="用户名"
      style="width: 140px"
      clearable
    />
    <el-input
      v-model="addForm.password"
      type="password"
      placeholder="密码 (至少6位)"
      style="width: 170px"
      show-password
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
