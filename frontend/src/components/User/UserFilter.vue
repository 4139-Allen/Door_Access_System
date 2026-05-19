<template>
  <div class="filter-form">
    <el-input
      v-model="filterForm.username"
      placeholder="用户名"
      style="width: 170px"
      clearable
      size="default"
      @input="onInput"
      @keydown.enter="search"
    />
    <el-button type="primary" @click="search">搜索</el-button>
    <el-button @click="reset">重置</el-button>
  </div>
</template>

<script setup>
let debounceTimer = null

defineProps({ filterForm: { type: Object, required: true } })
const emit = defineEmits(['search', 'reset'])

const onInput = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => emit('search'), 300)
}

const search = () => emit('search')
const reset = () => {
  clearTimeout(debounceTimer)
  emit('reset')
}
</script>

<style scoped>
.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
</style>
