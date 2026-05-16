<template>
  <el-card>
    <h2>设备管理</h2>
    <el-divider />

    <!-- 筛选区域 + 阻止回车默认提交 -->
    <el-form
      :model="filterForm"
      inline
      style="margin-bottom: 20px"
      @submit.prevent="resetPageAndSearch"
    >
      <el-form-item label="设备名称">
        <el-input
          v-model="filterForm.name"
          placeholder="输入设备名称搜索"
          style="width: 280px"
          clearable
          @keydown.enter.exact="resetPageAndSearch"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="resetPageAndSearch">搜索</el-button>
        <el-button @click="resetFilter" style="margin-left: 10px">重置</el-button>
      </el-form-item>
    </el-form>

    <el-divider style="margin: 15px 0;"></el-divider>

    <!-- 新增设备 -->
    <el-form :model="addForm" inline style="margin-bottom: 20px">
      <el-form-item label="设备名称">
        <el-input v-model="addForm.name" style="width: 280px" />
      </el-form-item>
      <el-form-item label="设备位置">
        <el-input v-model="addForm.location" style="width: 280px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="addDevice">新增设备</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="deviceList" border>
      <el-table-column prop="id" label="ID" />
      <el-table-column prop="name" label="设备名称" />
      <el-table-column prop="location" label="位置" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button type="danger" size="small" @click="delDevice(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top: 20px; text-align: right"
      v-model:current-page="page"
      v-model:page-size="size"
      :total="total"
      layout="total, prev, pager, next, jumper"
      @current-change="getDeviceList"
      @size-change="getDeviceList"
    />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const page = ref(1)
const size = ref(10)
const total = ref(0)

const filterForm = ref({
  name: ''
})

const deviceList = ref([])
const addForm = ref({ name: '', location: '' })

const getDeviceList = async () => {
  try {
    const params = {
      page: page.value,
      size: size.value,
    }
    if (filterForm.value.name.trim() !== '') {
      params.name = filterForm.value.name.trim()
    }

    const res = await request.get('/devices', { params })

    deviceList.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error('获取设备失败', e)
  }
}

const resetPageAndSearch = () => {
  page.value = 1
  getDeviceList()
}

const resetFilter = () => {
  filterForm.value.name = ''
  page.value = 1
  getDeviceList()
}

const addDevice = async () => {
  try {
    const res = await request.post('/devices', addForm.value)
    if (res.code === 200) {
      ElMessage.success('新增设备成功')
      getDeviceList()
      addForm.value = { name: '', location: '' }
    } else {
      ElMessage.error(res.msg || '新增失败')
    }
  } catch (e) {
    const msg = e.response?.data?.msg || '新增失败'
    ElMessage.error(msg)
  }
}

const delDevice = async (id) => {
  try {
    await request.delete(`/devices/${id}`)
    ElMessage.success('删除成功')
    getDeviceList()
  } catch (e) {
    ElMessage.error('删除失败：请先解绑用户')
  }
}

onMounted(() => {
  getDeviceList()
})
</script>