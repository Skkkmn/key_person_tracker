<template>
  <div>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6" v-for="item in statCards" :key="item.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" :style="{ color: item.color }">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <el-form :inline="true" :model="query" size="small">
        <el-form-item label="预警等级">
          <el-select v-model="query.alert_level" placeholder="全部" clearable style="width:110px">
            <el-option label="紧急" value="urgent" />
            <el-option label="重要" value="important" />
            <el-option label="普通" value="normal" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width:110px">
            <el-option label="待处理" value="pending" />
            <el-option label="已处理" value="handled" />
            <el-option label="已撤销" value="dismissed" />
          </el-select>
        </el-form-item>
        <el-form-item label="人员姓名">
          <el-input v-model="query.person_name" placeholder="姓名" clearable style="width:120px" />
        </el-form-item>
        <el-form-item label="预警类型">
          <el-input v-model="query.alert_type" placeholder="类型" clearable style="width:120px" />
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker v-model="query.start_time" type="datetime" placeholder="开始" value-format="YYYY-MM-DD HH:mm:ss" style="width:150px" />
          <span style="margin:0 6px">~</span>
          <el-date-picker v-model="query.end_time" type="datetime" placeholder="结束" value-format="YYYY-MM-DD HH:mm:ss" style="width:150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="openDialog()">新增预警</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="person_name" label="人员姓名" width="90" />
        <el-table-column prop="alert_type" label="预警类型" width="110" />
        <el-table-column prop="alert_content" label="预警内容" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span @click="showDetail(row)" style="cursor:pointer;color:#409eff">{{ row.alert_content }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="alert_level" label="等级" width="65" align="center">
          <template #default="{ row }">
            <el-tag :type="levelType(row.alert_level)" size="small">{{ levelLabel(row.alert_level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alert_time" label="预警时间" width="150" />
        <el-table-column prop="status" label="状态" width="75" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="handler_name" label="处理人" width="75" />
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="showDetail(row)">详情</el-button>
            <el-button size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="warning" link @click="handleProcess(row)">处理</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:16px;text-align:right">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="perPage"
          :total="total"
          :page-sizes="[10,20,50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editMode ? '编辑预警' : '新增预警'" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="关联人员" prop="person_id">
          <el-select v-model="form.person_id" placeholder="选择人员" filterable style="width:100%">
            <el-option v-for="p in personList" :key="p.person_id" :label="`${p.name}(${p.id_card})`" :value="p.person_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="预警类型" prop="alert_type">
          <el-select v-model="form.alert_type" allow-create filterable default-first-option style="width:100%">
            <el-option label="行为异常" value="行为异常" />
            <el-option label="脱管风险" value="脱管风险" />
            <el-option label="病情波动" value="病情波动" />
            <el-option label="异常活动" value="异常活动" />
            <el-option label="出入境预警" value="出入境预警" />
            <el-option label="活动预警" value="活动预警" />
            <el-option label="网络预警" value="网络预警" />
            <el-option label="聚集预警" value="聚集预警" />
            <el-option label="肇事风险" value="肇事风险" />
            <el-option label="复吸风险" value="复吸风险" />
            <el-option label="再犯风险" value="再犯风险" />
            <el-option label="走失风险" value="走失风险" />
            <el-option label="异常轨迹" value="异常轨迹" />
            <el-option label="在所表现" value="在所表现" />
          </el-select>
        </el-form-item>
        <el-form-item label="预警等级">
          <el-select v-model="form.alert_level" style="width:100%">
            <el-option label="紧急" value="urgent" />
            <el-option label="重要" value="important" />
            <el-option label="普通" value="normal" />
          </el-select>
        </el-form-item>
        <el-form-item label="预警时间">
          <el-date-picker v-model="form.alert_time" type="datetime" style="width:100%" value-format="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item label="预警内容" prop="alert_content">
          <el-input v-model="form.alert_content" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="processVisible" title="处理预警" width="500px">
      <el-form ref="processFormRef" :model="processForm" label-width="80px">
        <el-form-item label="处理结果"><el-input v-model="processForm.handle_result" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="processForm.status" style="width:100%">
            <el-option label="已处理" value="handled" />
            <el-option label="已撤销" value="dismissed" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="processVisible = false">取消</el-button>
        <el-button type="primary" :loading="processLoading" @click="handleProcessSubmit">确认</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailVisible" title="预警详情" size="500px">
      <template v-if="detailData">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="人员姓名">{{ detailData.person_name }}</el-descriptions-item>
          <el-descriptions-item label="预警类型">{{ detailData.alert_type }}</el-descriptions-item>
          <el-descriptions-item label="预警等级">
            <el-tag :type="levelType(detailData.alert_level)" size="small">{{ levelLabel(detailData.alert_level) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预警时间">{{ detailData.alert_time }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(detailData.status)" size="small">{{ statusLabel(detailData.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="处理人">{{ detailData.handler_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="处理时间">{{ detailData.handle_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="处理结果">{{ detailData.handle_result || '-' }}</el-descriptions-item>
          <el-descriptions-item label="预警内容" content-style="white-space:pre-wrap">{{ detailData.alert_content }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listAlerts, getAlertStats, createAlert, updateAlert, deleteAlert, handleAlert } from '../api/personAlert'
import { getAllPersons } from '../api/keyPerson'

const personList = ref([])
const tableData = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const perPage = ref(10)
const dialogVisible = ref(false)
const editMode = ref(false)
const currentId = ref(null)
const submitLoading = ref(false)
const formRef = ref(null)
const processVisible = ref(false)
const processLoading = ref(false)
const processFormRef = ref(null)
const processAlertId = ref(null)
const detailVisible = ref(false)
const detailData = ref(null)

const statCards = ref([
  { label: '待处理预警', value: 0, color: '#e6a23c' },
  { label: '紧急待处理', value: 0, color: '#f56c6c' },
  { label: '预警总数', value: 0, color: '#409eff' },
])

const query = reactive({
  alert_level: '', status: '', person_name: '', alert_type: '',
  start_time: '', end_time: '',
})

const form = reactive({ person_id: null, alert_type: '', alert_level: 'normal', alert_content: '', alert_time: '' })
const processForm = reactive({ handle_result: '', status: 'handled' })
const rules = {
  person_id: [{ required: true, message: '请选择人员', trigger: 'change' }],
  alert_type: [{ required: true, message: '请输入预警类型', trigger: 'change' }],
  alert_content: [{ required: true, message: '请输入预警内容', trigger: 'blur' }],
}

function nowStr() {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

onMounted(async () => {
  const [personRes, statRes] = await Promise.all([
    getAllPersons(),
    getAlertStats(),
  ])
  if (personRes.code === 200) personList.value = personRes.data
  if (statRes.code === 200) {
    statCards.value[0].value = statRes.data.pending
    statCards.value[1].value = statRes.data.urgent_pending
    statCards.value[2].value = statRes.data.total
  }
  fetchData()
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await listAlerts({ ...query, page: page.value, per_page: perPage.value })
    if (res.code === 200) {
      tableData.value = res.data.items
      total.value = res.data.total
    }
  } finally { loading.value = false }
}

const handleSearch = () => { page.value = 1; fetchData() }
const handleReset = () => {
  Object.assign(query, { alert_level: '', status: '', person_name: '', alert_type: '', start_time: '', end_time: '' })
  page.value = 1
  fetchData()
}

const openDialog = (row) => {
  editMode.value = !!row
  currentId.value = row ? row.alert_id : null
  if (row) {
    Object.assign(form, { person_id: row.person_id, alert_type: row.alert_type, alert_level: row.alert_level, alert_content: row.alert_content, alert_time: row.alert_time })
  } else {
    Object.assign(form, { person_id: null, alert_type: '', alert_level: 'normal', alert_content: '', alert_time: nowStr() })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const res = editMode.value ? await updateAlert(currentId.value, form) : await createAlert(form)
    if (res.code === 200) { ElMessage.success('操作成功'); dialogVisible.value = false; fetchData(); refreshStats() }
  } finally { submitLoading.value = false }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该预警？', '提示')
    const res = await deleteAlert(row.alert_id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchData(); refreshStats() }
  } catch {}
}

const handleProcess = (row) => {
  processAlertId.value = row.alert_id
  processForm.handle_result = ''
  processForm.status = 'handled'
  processVisible.value = true
}

const handleProcessSubmit = async () => {
  processLoading.value = true
  try {
    const res = await handleAlert(processAlertId.value, processForm)
    if (res.code === 200) { ElMessage.success('处理成功'); processVisible.value = false; fetchData(); refreshStats() }
  } finally { processLoading.value = false }
}

const showDetail = (row) => {
  detailData.value = row
  detailVisible.value = true
}

const refreshStats = async () => {
  const statRes = await getAlertStats()
  if (statRes.code === 200) {
    statCards.value[0].value = statRes.data.pending
    statCards.value[1].value = statRes.data.urgent_pending
    statCards.value[2].value = statRes.data.total
  }
}

const levelType = (v) => ({ urgent: 'danger', important: 'warning', normal: 'info' }[v] || 'info')
const levelLabel = (v) => ({ urgent: '紧急', important: '重要', normal: '普通' }[v] || v)
const statusType = (v) => ({ pending: 'danger', handled: 'success', dismissed: 'info' }[v] || 'info')
const statusLabel = (v) => ({ pending: '待处理', handled: '已处理', dismissed: '已撤销' }[v] || v)
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 32px; font-weight: bold; }
.stat-label { margin-top: 6px; color: #909399; font-size: 14px; }
</style>
