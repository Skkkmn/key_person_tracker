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
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width:110px">
            <el-option label="待分配" value="pending" />
            <el-option label="执行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="query.task_type" placeholder="全部" clearable style="width:110px">
            <el-option label="日常走访" value="daily" />
            <el-option label="每周走访" value="weekly" />
            <el-option label="月度回访" value="monthly" />
            <el-option label="临时任务" value="temp" />
            <el-option label="常规任务" value="routine" />
          </el-select>
        </el-form-item>
        <el-form-item label="人员">
          <el-select v-model="query.person_id" placeholder="选择人员" clearable filterable style="width:150px">
            <el-option v-for="p in personList" :key="p.person_id" :label="p.name" :value="p.person_id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="openDialog()">新建任务</el-button>
          <el-button @click="handleAutoGenerate">自动生成</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="person_name" label="人员" width="80" />
        <el-table-column prop="title" label="任务标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="task_type" label="类型" width="85" align="center">
          <template #default="{ row }">
            <el-tag :type="taskTypeTag(row.task_type)" size="small">{{ taskTypeLabel(row.task_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignee_name" label="负责人" width="80" />
        <el-table-column prop="deadline" label="截止时间" width="150" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="showDetail(row)">详情</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button v-if="row.status === 'pending' || row.status === 'in_progress'" size="small" type="success" link @click="handleExecute(row)">执行走访</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="warning" link @click="handleAssign(row)">分配</el-button>
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

    <el-dialog v-model="dialogVisible" :title="editMode ? '编辑任务' : '新建任务'" width="550px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="关联人员" prop="person_id">
          <el-select v-model="form.person_id" placeholder="选择人员" filterable style="width:100%">
            <el-option v-for="p in personList" :key="p.person_id" :label="`${p.name}(${p.id_card})`" :value="p.person_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="form.task_type" style="width:100%">
            <el-option label="日常走访" value="daily" />
            <el-option label="每周走访" value="weekly" />
            <el-option label="月度回访" value="monthly" />
            <el-option label="临时任务" value="temp" />
            <el-option label="常规任务" value="routine" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="form.assigned_to" placeholder="可选" filterable clearable style="width:100%">
            <el-option v-for="u in userList" :key="u.user_id" :label="u.real_name || u.username" :value="u.user_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker v-model="form.deadline" type="datetime" style="width:100%" value-format="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="assignVisible" title="分配任务" width="400px">
      <el-form ref="assignFormRef" :model="assignForm" label-width="70px">
        <el-form-item label="负责人" prop="assigned_to">
          <el-select v-model="assignForm.assigned_to" placeholder="选择负责人" filterable style="width:100%">
            <el-option v-for="u in userList" :key="u.user_id" :label="u.real_name || u.username" :value="u.user_id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" :loading="assignLoading" @click="handleAssignSubmit">确认分配</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailVisible" title="任务详情" size="500px">
      <template v-if="detailData">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="人员姓名">{{ detailData.person_name }}</el-descriptions-item>
          <el-descriptions-item label="任务标题">{{ detailData.title }}</el-descriptions-item>
          <el-descriptions-item label="任务描述">{{ detailData.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">
            <el-tag :type="taskTypeTag(detailData.task_type)" size="small">{{ taskTypeLabel(detailData.task_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusTag(detailData.status)" size="small">{{ statusLabel(detailData.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="负责人">{{ detailData.assignee_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分配人">{{ detailData.assigner_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分配时间">{{ detailData.assign_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="截止时间">{{ detailData.deadline || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ detailData.created_at }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { listVisitTasks, getVisitTaskStats, createVisitTask, updateVisitTask, deleteVisitTask, autoGenerateTasks } from '../api/visitTask'
import { getAllPersons } from '../api/keyPerson'
import { listUsers } from '../api/user'

const router = useRouter()
const personList = ref([])
const userList = ref([])
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
const assignVisible = ref(false)
const assignLoading = ref(false)
const assignFormRef = ref(null)
const assignTaskId = ref(null)
const detailVisible = ref(false)
const detailData = ref(null)

const statCards = ref([
  { label: '待分配任务', value: 0, color: '#e6a23c' },
  { label: '执行中', value: 0, color: '#409eff' },
  { label: '已完成', value: 0, color: '#67c23a' },
  { label: '已逾期', value: 0, color: '#f56c6c' },
])

const query = reactive({ status: '', task_type: '', person_id: null })

const form = reactive({ person_id: null, title: '', description: '', task_type: 'routine', assigned_to: null, deadline: '' })
const assignForm = reactive({ assigned_to: null })

const rules = {
  person_id: [{ required: true, message: '请选择人员', trigger: 'change' }],
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
}

onMounted(async () => {
  const [personRes, userRes] = await Promise.all([getAllPersons(), listUsers()])
  if (personRes.code === 200) personList.value = personRes.data
  if (userRes.code === 200) userList.value = userRes.data
  fetchData()
  refreshStats()
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await listVisitTasks({ ...query, page: page.value, per_page: perPage.value })
    if (res.code === 200) {
      tableData.value = res.data.items
      total.value = res.data.total
    }
  } finally { loading.value = false }
}

const refreshStats = async () => {
  const res = await getVisitTaskStats()
  if (res.code === 200) {
    statCards.value[0].value = res.data.pending
    statCards.value[1].value = res.data.in_progress
    statCards.value[2].value = res.data.completed
    statCards.value[3].value = res.data.overdue
  }
}

const handleSearch = () => { page.value = 1; fetchData() }
const handleReset = () => {
  Object.assign(query, { status: '', task_type: '', person_id: null })
  page.value = 1; fetchData()
}

const openDialog = (row) => {
  editMode.value = !!row
  currentId.value = row ? row.task_id : null
  if (row) {
    Object.assign(form, {
      person_id: row.person_id, title: row.title, description: row.description,
      task_type: row.task_type, assigned_to: row.assigned_to, deadline: toPicker(row.deadline),
    })
  } else {
    Object.assign(form, { person_id: null, title: '', description: '', task_type: 'routine', assigned_to: null, deadline: '' })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const res = editMode.value ? await updateVisitTask(currentId.value, form) : await createVisitTask(form)
    if (res.code === 200) { ElMessage.success('操作成功'); dialogVisible.value = false; fetchData(); refreshStats() }
  } finally { submitLoading.value = false }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该任务？', '提示')
    const res = await deleteVisitTask(row.task_id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchData(); refreshStats() }
  } catch {}
}

const handleAssign = (row) => {
  assignTaskId.value = row.task_id
  assignForm.assigned_to = row.assigned_to ?? null
  assignVisible.value = true
}

const handleAssignSubmit = async () => {
  assignLoading.value = true
  try {
    if (!assignForm.assigned_to) { ElMessage.warning('请选择负责人'); return }
    const res = await updateVisitTask(assignTaskId.value, { assigned_to: assignForm.assigned_to, status: 'in_progress' })
    if (res.code === 200) { ElMessage.success('分配成功'); assignVisible.value = false; fetchData() }
  } finally { assignLoading.value = false }
}

const handleExecute = (row) => {
  router.push({ name: 'VisitRecordForm', params: { taskId: row.task_id } })
}

const handleAutoGenerate = async () => {
  try {
    await ElMessageBox.confirm('将根据风险等级自动生成走访任务，确认继续？', '提示')
    const res = await autoGenerateTasks()
    if (res.code === 200) { ElMessage.success(res.message); fetchData(); refreshStats() }
  } catch {}
}

const showDetail = (row) => {
  detailData.value = row
  detailVisible.value = true
}

const taskTypeTag = (v) => ({ daily: 'danger', weekly: 'warning', monthly: 'info', temp: 'primary', routine: '' }[v] || '')
const taskTypeLabel = (v) => ({ daily: '日常', weekly: '每周', monthly: '月度', temp: '临时', routine: '常规' }[v] || v)
const statusTag = (v) => ({ pending: 'info', in_progress: 'warning', completed: 'success', cancelled: 'danger' }[v] || 'info')
const statusLabel = (v) => ({ pending: '待分配', in_progress: '执行中', completed: '已完成', cancelled: '已取消' }[v] || v)

function toPicker(dt) {
  return dt ? dt.replace('T', ' ').substring(0, 19) : ''
}
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 32px; font-weight: bold; }
.stat-label { margin-top: 6px; color: #909399; font-size: 14px; }
</style>
