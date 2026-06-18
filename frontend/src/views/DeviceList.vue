<template>
  <div>
    <el-card>
      <el-form :inline="true" size="small">
        <el-form-item label="状态">
          <el-select v-model="filters.is_active" clearable placeholder="全部" style="width:100px">
            <el-option label="启用" :value="1" /><el-option label="停用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button type="success" @click="showBindDialog" v-if="userStore.roleLevel >= 3">绑定设备</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <el-table :data="devices" v-loading="loading" border stripe size="small">
        <el-table-column prop="device_id" label="ID" width="60" />
        <el-table-column prop="person_name" label="绑定人员" min-width="120" />
        <el-table-column prop="device_name" label="设备名称" width="150" />
        <el-table-column prop="phone_number" label="手机号" width="130" />
        <el-table-column prop="last_battery_level" label="电量" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.last_battery_level != null" :type="batteryType(row.last_battery_level)" size="small">
              {{ row.last_battery_level }}%
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_online_at" label="最后在线" width="160">
          <template #default="{ row }">
            {{ row.last_online_at ? formatTime(row.last_online_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后位置" min-width="180">
          <template #default="{ row }">
            <span v-if="row.last_latitude && row.last_longitude" style="font-size:12px;color:#666">
              {{ row.last_latitude.toFixed(4) }}, {{ row.last_longitude.toFixed(4) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确认解绑？" @confirm="handleUnbind(row.device_id)" v-if="userStore.roleLevel >= 3">
              <template #reference>
                <el-button type="danger" size="small" link>解绑</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="perPage"
        :total="total"
        layout="total, prev, pager, next"
        small
        style="margin-top:12px;justify-content:center"
        @current-change="loadData"
      />
    </el-card>

    <el-dialog v-model="bindVisible" title="绑定定位设备" width="500px">
      <el-form ref="bindFormRef" :model="bindForm" :rules="bindRules" label-width="100px">
        <el-form-item label="重点人员" prop="person_id">
          <el-select v-model="bindForm.person_id" filterable remote :remote-method="searchPerson" :loading="personLoading" placeholder="搜索姓名/身份证" style="width:100%">
            <el-option v-for="p in personOptions" :key="p.person_id" :label="`${p.name} (${p.id_card})`" :value="p.person_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备名称" prop="device_name">
          <el-input v-model="bindForm.device_name" placeholder="如: 张三的手机" />
        </el-form-item>
        <el-form-item label="IMEI" prop="device_imei">
          <el-input v-model="bindForm.device_imei" placeholder="手机IMEI号" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone_number">
          <el-input v-model="bindForm.phone_number" placeholder="手机号码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bindVisible = false">取消</el-button>
        <el-button type="primary" :loading="bindLoading" @click="handleBind">确认绑定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listDevices, bindDevice, unbindDevice } from '../api/device'
import { listPersons } from '../api/keyPerson'
import { useUserStore } from '../store'

const userStore = useUserStore()
const loading = ref(false)
const devices = ref([])
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const filters = reactive({ is_active: '' })
const bindVisible = ref(false)
const bindLoading = ref(false)
const bindFormRef = ref(null)
const personOptions = ref([])
const personLoading = ref(false)

const bindForm = reactive({
  person_id: '',
  device_name: '',
  device_imei: '',
  phone_number: '',
})

const bindRules = {
  person_id: [{ required: true, message: '请选择人员', trigger: 'change' }],
}

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (filters.is_active !== '' && filters.is_active !== null) {
      params.is_active = filters.is_active
    }
    const res = await listDevices(params)
    if (res.code === 200) {
      devices.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch { devices.value = []; total.value = 0 }
  finally { loading.value = false }
}

async function searchPerson(query) {
  if (!query) return
  personLoading.value = true
  try {
    const res = await listPersons({ name: query, per_page: 10 })
    if (res.code === 200) {
      personOptions.value = res.data.items || []
    }
  } catch { personOptions.value = [] }
  finally { personLoading.value = false }
}

function showBindDialog() {
  bindForm.person_id = ''
  bindForm.device_name = ''
  bindForm.device_imei = ''
  bindForm.phone_number = ''
  personOptions.value = []
  bindVisible.value = true
}

async function handleBind() {
  const valid = await bindFormRef.value.validate().catch(() => false)
  if (!valid) return
  bindLoading.value = true
  try {
    const res = await bindDevice(bindForm)
    if (res.code === 200) {
      ElMessage.success('绑定成功')
      bindVisible.value = false
      loadData()
    }
  } finally { bindLoading.value = false }
}

async function handleUnbind(deviceId) {
  try {
    const res = await unbindDevice(deviceId)
    if (res.code === 200) {
      ElMessage.success('解绑成功')
      loadData()
    }
  } catch {}
}

function formatTime(t) {
  if (!t) return '-'
  const d = new Date(t)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const batteryType = (v) => v > 50 ? 'success' : v > 20 ? 'warning' : 'danger'
</script>
