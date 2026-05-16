<template>
  <el-card>
    <h2>门禁开门日志</h2>
    <el-divider />

    <!-- 管理员日志筛选区域 -->
    <el-form :model="filterForm" inline style="margin-bottom:20px;">
      <el-form-item label="用户ID">
        <el-input
          v-model="filterForm.user_id"
          placeholder="搜索用户ID"
          style="width: 160px"
          clearable
        />
      </el-form-item>

      <el-form-item label="设备名称">
        <el-input
          v-model="filterForm.device_name"
          placeholder="搜索设备名称"
          style="width: 200px"
          clearable
        />
      </el-form-item>

      <el-form-item label="操作状态">
        <el-select
          v-model="filterForm.status"
          placeholder="全部状态"
          style="width: 160px"
          clearable
        >
          <el-option label="成功" value="成功" />
          <el-option label="失败" value="失败" />
        </el-select>
      </el-form-item>

      <el-form-item label="操作时间">
        <el-date-picker
          v-model="filterForm.time_range"
          type="daterange"
          range-separator="~"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          style="width: 380px"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="resetPageAndSearch">搜索</el-button>
        <el-button @click="resetFilter" style="margin-left:10px">重置</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="logList" border stripe>
      <el-table-column label="ID" prop="id" />
      <el-table-column label="用户ID" prop="user_id" />
      <el-table-column label="设备名称" prop="device_name" />
      <el-table-column label="设备位置" prop="device_location" />
      <el-table-column label="操作" prop="action" />
      <el-table-column label="状态" prop="status" />
      <el-table-column label="时间" prop="time" />
    </el-table>

    <el-pagination
      v-model:current-page="page"
      v-model:page-size="size"
      :total="total"
      layout="total, prev, pager, next, jumper"
      style="margin-top:20px; text-align:right"
      @current-change="getLogList"
      @size-change="getLogList"
      :locale="{
        prevText: '上一页',
        nextText: '下一页',
        total: '共 {total} 条',
        goto: '前往',
        pageClassifier: '页'
      }"
    />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const logList = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)

// 筛选条件
const filterForm = ref({
  user_id: '',
  device_name: '',
  status: '',
  time_range: []
})

// 获取日志（带筛选）
const getLogList = async () => {
  try {
    const params = {
      page: page.value,
      size: size.value
    }

    // 只在有值时才添加筛选参数
    if (filterForm.value.user_id && filterForm.value.user_id.toString().trim() !== '') {
      params.user_id = parseInt(filterForm.value.user_id)
    }

    if (filterForm.value.device_name && filterForm.value.device_name.trim() !== '') {
      params.device_name = filterForm.value.device_name.trim()
    }

    if (filterForm.value.status && filterForm.value.status.trim() !== '') {
      params.status = filterForm.value.status
    }

    // 时间范围
    if (filterForm.value.time_range && filterForm.value.time_range.length === 2) {
      params.start_time = filterForm.value.time_range[0]
      params.end_time = filterForm.value.time_range[1]
    }

    const res = await request.get('/door-logs', { params })
    logList.value = res.data.list
    total.value = res.data.total
  } catch (e) {
    console.error('日志加载失败', e)
  }
}

// 搜索 → 回到第一页
const resetPageAndSearch = () => {
  page.value = 1
  getLogList()
}

// 重置筛选
const resetFilter = () => {
  filterForm.value = {
    user_id: '',
    device_name: '',
    status: '',
    time_range: []
  }
  page.value = 1
  getLogList()
}

onMounted(() => {
  getLogList()
})
</script>