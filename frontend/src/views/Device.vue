<template>
  <div class="device-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <div>
          <h2 class="header-title">设备管理</h2>
          <p class="header-desc">管理门禁设备与监控设备运行状态</p>
        </div>
      </div>
      <div class="header-right">
        <span class="total-count">共 {{ total }} 台设备</span>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar-card">
      <div class="toolbar-section">
        <div class="section-label">搜索</div>
        <DeviceFilter
          :filter-form="filterForm"
          @search="resetPageAndSearch"
          @reset="resetFilter"
        />
      </div>

      <div class="toolbar-divider"></div>

      <div class="toolbar-section">
        <div class="section-label">新增设备</div>
        <DeviceAddForm
          :add-form="addForm"
          :loading="adding"
          @add="addDevice"
        />
      </div>
    </div>

    <!-- 设备列表 -->
    <div class="table-card">
      <div class="table-header">
        <span class="table-header-title">设备列表</span>
        <el-tag size="small" type="info" effect="plain">
          共 {{ total }} 条记录
        </el-tag>
      </div>

      <DeviceTable
        :device-list="deviceList"
        :total="total"
        :loading="loading"
        v-model:page="page"
        v-model:size="size"
        @edit="editDevice"
        @delete="delDevice"
      />
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑设备" width="450px" top="30vh">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="80px">
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="editForm.name" placeholder="输入设备名称" />
        </el-form-item>
        <el-form-item label="设备位置" prop="location">
          <el-input v-model="editForm.location" placeholder="输入设备位置" />
        </el-form-item>
        <el-form-item label="设备状态">
          <el-switch
            v-model="editForm.status"
            active-value="online"
            inactive-value="offline"
            active-text="在线"
            inactive-text="离线"
            style="--el-switch-on-color: #22c55e"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import DeviceFilter from '@/components/Device/DeviceFilter.vue'
import DeviceAddForm from '@/components/Device/DeviceAddForm.vue'
import DeviceTable from '@/components/Device/DeviceTable.vue'

const page = ref(1)
const size = ref(10)
const total = ref(0)
const loading = ref(false)

const filterForm = ref({ name: '' })
const deviceList = ref([])
const addForm = ref({ name: '', location: '' })
const adding = ref(false)

const editDialogVisible = ref(false)
const editLoading = ref(false)
const editForm = ref({ id: null, name: '', location: '', status: 'offline' })
const editFormRef = ref(null)
const editRules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  location: [{ required: true, message: '请输入设备位置', trigger: 'blur' }]
}

watch([page, size], () => {
  getDeviceList()
})

const getDeviceList = async () => {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value }
    if (filterForm.value.name.trim()) {
      params.name = filterForm.value.name.trim()
    }
    const res = await request.get('/devices', { params })
    deviceList.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error('获取设备失败', e)
  } finally {
    loading.value = false
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
  if (!addForm.value.name || !addForm.value.location) {
    ElMessage.warning('请输入设备名称和位置')
    return
  }
  adding.value = true
  try {
    const res = await request.post('/devices', addForm.value)
    if (res.code === 200) {
      ElMessage.success('新增成功')
      getDeviceList()
      addForm.value = { name: '', location: '' }
    } else {
      ElMessage.error(res.msg || '新增失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '新增失败')
  } finally {
    adding.value = false
  }
}

const editDevice = (row) => {
  editForm.value = {
    id: row.id,
    name: row.name,
    location: row.location,
    status: row.status || 'offline'
  }
  editDialogVisible.value = true
}

const saveEdit = async () => {
  if (!editFormRef.value) return
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return
  editLoading.value = true
  try {
    const res = await request.put(`/devices/${editForm.value.id}`, {
      name: editForm.value.name,
      location: editForm.value.location,
      status: editForm.value.status
    })
    if (res.code === 200) {
      ElMessage.success('更新成功')
      editDialogVisible.value = false
      getDeviceList()
    } else {
      ElMessage.error(res.msg || '更新失败')
    }
  } catch (e) {
    ElMessage.error('更新失败')
  } finally {
    editLoading.value = false
  }
}

const delDevice = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该设备吗？请先确保已解绑所有用户。', '确认删除', {
      type: 'warning',
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    })
    await request.delete(`/devices/${id}`)
    ElMessage.success('删除成功')
    getDeviceList()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败：请先解绑用户')
    }
  }
}

onMounted(() => getDeviceList())
</script>

<style scoped>
.device-page {
  padding: 4px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px 24px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-desc {
  margin: 4px 0 0;
  font-size: 13px;
  color: #909399;
}

.total-count {
  font-size: 14px;
  color: #606266;
}

.toolbar-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  overflow: hidden;
}

.toolbar-section {
  flex: 1;
  min-width: 280px;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: #909399;
}

.toolbar-divider {
  width: 1px;
  align-self: stretch;
  background: #ebeef5;
  flex-shrink: 0;
}

.table-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid #ebeef5;
}

.table-header-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

@media (max-width: 900px) {
  .toolbar-divider {
    display: none;
  }
  .toolbar-section {
    min-width: 100%;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
