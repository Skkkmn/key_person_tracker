<template>
  <div>
    <el-card>
      <el-form :inline="true" :model="query" size="small">
        <el-form-item label="流动方向">
          <el-select v-model="query.direction" clearable placeholder="全部" style="width:110px">
            <el-option label="流入" value="in" /><el-option label="流出" value="out" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:110px">
            <el-option label="待处理" value="pending" /><el-option label="已确认" value="confirmed" /><el-option label="已忽略" value="dismissed" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="姓名/身份证" clearable style="width:160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="dialogVisible = true">新增流动记录</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="person_name" label="姓名" width="80" />
        <el-table-column prop="id_card" label="身份证号" width="160" />
        <el-table-column prop="direction" label="方向" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'in' ? 'success' : 'warning'" size="small">{{ row.direction === 'in' ? '流入' : '流出' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="from_dept_name" label="来源部门" min-width="120" />
        <el-table-column prop="to_dept_name" label="目标部门" min-width="120" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notified" label="推送" width="60" align="center">
          <template #default="{ row }">
            <el-tag :type="row.notified ? 'success' : 'info'" size="small">{{ row.notified ? '已推' : '未推' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detected_at" label="发现时间" width="150" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openDetail(row)">详情</el-button>
            <el-button v-if="!row.notified" size="small" type="warning" link @click="handlePush(row)">推送</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:16px;text-align:right">
        <el-pagination v-model:current-page="page" v-model:page-size="perPage" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @size-change="fetchData" @current-change="fetchData" />
      </div>
    </el-card>

    <el-dialog v-model="detailVisible" title="流动记录详情" width="600px">
      <template v-if="currentRow">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="姓名">{{ currentRow.person_name }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ currentRow.id_card }}</el-descriptions-item>
          <el-descriptions-item label="方向">
            <el-tag :type="currentRow.direction === 'in' ? 'success' : 'warning'" size="small">{{ currentRow.direction === 'in' ? '流入' : '流出' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(currentRow.status)" size="small">{{ statusLabel(currentRow.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="来源部门">{{ currentRow.from_dept_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="目标部门">{{ currentRow.to_dept_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="发现人">{{ currentRow.detector_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="发现时间">{{ currentRow.detected_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="推送状态">{{ currentRow.notified ? '已推送' : '未推送' }}</el-descriptions-item>
          <el-descriptions-item label="推送时间">{{ currentRow.notified_at || '-' }}</el-descriptions-item>
        </el-descriptions>
        <el-form style="margin-top:16px" label-width="80px">
          <el-form-item label="状态修改">
            <el-select v-model="detailStatus" style="width:200px">
              <el-option label="待处理" value="pending" /><el-option label="已确认" value="confirmed" /><el-option label="已忽略" value="dismissed" />
            </el-select>
            <el-button type="primary" size="small" style="margin-left:8px" @click="handleUpdateStatus">确认修改</el-button>
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="detailRemark" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
      </template>
    </el-dialog>

    <el-dialog v-model="dialogVisible" title="新增流动记录" width="500px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="80px">
        <el-form-item label="人员" prop="person_id">
          <el-select v-model="form.person_id" filterable remote :remote-method="searchPerson" placeholder="搜索姓名/身份证" style="width:100%">
            <el-option v-for="p in personOptions" :key="p.person_id" :label="`${p.name} (${p.id_card})`" :value="p.person_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="流动方向" prop="direction">
          <el-radio-group v-model="form.direction">
            <el-radio value="in">流入</el-radio>
            <el-radio value="out">流出</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="目标部门" prop="to_dept_id">
          <el-select v-model="form.to_dept_id" placeholder="请选择" clearable style="width:100%">
            <el-option v-for="d in departments" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确认创建并推送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listCrossRegionTracks, createCrossRegionTrack, updateCrossRegionTrack, deleteCrossRegionTrack, pushCrossRegionNotification } from '../api/crossRegion'
import { listPersons } from '../api/keyPerson'
import { listDepartments } from '../api/department'

const tableData = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const perPage = ref(10)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const submitLoading = ref(false)
const currentRow = ref(null)
const formRef = ref(null)
const departments = ref([])
const personOptions = ref([])
const detailStatus = ref('pending')
const detailRemark = ref('')

const query = reactive({ direction: '', status: '', keyword: '' })

const form = reactive({ person_id: null, direction: 'in', to_dept_id: null, remark: '' })
const formRules = {
  person_id: [{ required: true, message: '请选择人员', trigger: 'change' }],
  direction: [{ required: true, message: '请选择流动方向', trigger: 'change' }],
  to_dept_id: [{ required: true, message: '请选择目标部门', trigger: 'change' }],
}

onMounted(async () => {
  const deptRes = await listDepartments({ status: 1 })
  if (deptRes.code === 200) departments.value = deptRes.data
  fetchData()
})

async function searchPerson(keyword) {
  if (!keyword) return
  const res = await listPersons({ keyword, per_page: 20 })
  if (res.code === 200) personOptions.value = res.data.items
}

async function fetchData() {
  loading.value = true
  try {
    const params = { ...query, page: page.value, per_page: perPage.value }
    const res = await listCrossRegionTracks(params)
    if (res.code === 200) { tableData.value = res.data.items; total.value = res.data.total }
  } finally { loading.value = false }
}

const handleSearch = () => { page.value = 1; fetchData() }
const handleReset = () => { Object.assign(query, { direction: '', status: '', keyword: '' }); page.value = 1; fetchData() }

const openDetail = (row) => {
  currentRow.value = row
  detailStatus.value = row.status
  detailRemark.value = row.remark || ''
  detailVisible.value = true
}

const handleUpdateStatus = async () => {
  await updateCrossRegionTrack(currentRow.value.track_id, { status: detailStatus.value, remark: detailRemark.value })
  ElMessage.success('状态已更新')
  detailVisible.value = false
  fetchData()
}

const handlePush = async (row) => {
  try {
    await ElMessageBox.confirm(`确认向目标部门推送 ${row.person_name} 的流动通知？`, '提示')
    const res = await pushCrossRegionNotification(row.track_id)
    if (res.code === 200) { ElMessage.success('推送成功'); fetchData() }
  } catch {}
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除 ${row.person_name} 的流动记录？`, '提示')
    await deleteCrossRegionTrack(row.track_id)
    ElMessage.success('删除成功')
    fetchData()
  } catch {}
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const res = await createCrossRegionTrack(form)
    if (res.code === 200) {
      ElMessage.success('创建成功，已推送通知')
      dialogVisible.value = false
      fetchData()
    }
  } finally { submitLoading.value = false }
}

const statusType = (v) => ({ pending: 'warning', confirmed: 'success', dismissed: 'info' }[v] || 'info')
const statusLabel = (v) => ({ pending: '待处理', confirmed: '已确认', dismissed: '已忽略' }[v] || v)
</script>
