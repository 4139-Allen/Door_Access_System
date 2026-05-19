<template>
  <div class="bind-form">
    <el-input v-model="bindForm.user_id" placeholder="用户ID" style="width: 120px" clearable />
    <el-input v-model="bindForm.device_id" placeholder="设备ID" style="width: 120px" clearable />
    <el-button type="success" @click="$emit('bind')" :loading="bindLoading">绑定</el-button>
    <el-button type="danger" plain @click="$emit('unbind')" :loading="unbindLoading">解绑</el-button>
  </div>
</template>

<script setup>
defineProps({
  bindForm: { type: Object, required: true },
  bindLoading: { type: Boolean, default: false },
  unbindLoading: { type: Boolean, default: false }
})
const emit = defineEmits(['bind', 'unbind'])
</script>

<style scoped>
.bind-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
</style>
