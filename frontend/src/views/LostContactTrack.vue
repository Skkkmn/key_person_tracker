<template>
  <div>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="8" v-for="item in statCards" :key="item.label">
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
            <el-option label="追踪中" value="tracking" />
            <el-option label="已找到" value="resolved" />
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
          <el-button type="success" @click="openDialog()">新建台账</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="person_name" label="姓名" width="80" />
        <el-table-column prop="lost_time" label="失联时间" width="150" />
        <el-table-column prop="last_location" label="最后出现地点" min-width="160" show-overflow-tooltip />
        <el-table-column prop="search_measures" label="查找措施" min-width="180" show-overflow-tooltip />
        <el-table-column prop="progress" label="进展" min-width="180" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'resolved' ? 'success' : 'danger'" size="small">{{ row.status === 'resolved' ? '已找到' : '追踪中' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="230" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="showDetail(row)">详情</el-button>
            <el-button size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button v-if="row.status === 'tracking'" size="small" type="success" link @click="handleResolve(row)">已找到</el-button>
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

    <el-dialog v-model="dialogVisible" :title="editMode ? '编辑台账' : '新建台账'" width="550px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="关联人员" prop="person_id">
          <el-select v-model="form.person_id" placeholder="选择人员" filterable :disabled="editMode" style="width:100%">
            <el-option v-for="p in personList" :key="p.person_id" :label="`${p.name}(${p.id_card})`" :value="p.person_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="失联时间">
          <el-date-picker v-model="form.lost_time" type="datetime" style="width:100%" value-format="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item label="最后出现地点">
          <el-input v-model="form.last_location" />
        </el-form-item>
        <el-form-item label="查找措施">
          <el-input v-model="form.search_measures" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="家属联系方式">
          <el-input v-model="form.family_contact" />
        </el-form-item>
        <el-form-item label="当前进展">
          <el-input v-model="form.progress" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item v-if="editMode" label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="追踪中" value="tracking" />
            <el-option label="已找到" value="resolved" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailVisible" title="失联追踪详情" size="500px">
      <template v-if="detailData">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="人员姓名">{{ detailData.person_name }}</el-descriptions-item>
          <el-descriptions-item label="失联时间">{{ detailData.lost_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="最后出现地点">{{ detailData.last_location || '-' }}</el-descriptions-item>
          <el-descriptions-item label="查找措施">{{ detailData.search_measures || '-' }}</el-descriptions-item>
          <el-descriptions-item label="家属联系方式">{{ detailData.family_contact || '-' }}</el-descriptions-item>
          <el-descriptions-item label="当前进展">{{ detailData.progress || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detailData.status === 'resolved' ? 'success' : 'danger'" size="small">{{ detailData.status === 'resolved' ? '已找到' : '追踪中' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="detailData.resolved_at" label="找到时间">{{ detailData.resolved_at }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ detailData.created_at }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listLostContactTracks, createLostContactTrack, updateLostContactTrack, deleteLostContactTrack } from '../api/lostContact'
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
const detailVisible = ref(false)
const detailData = ref(null)

const statCards = ref([
  { label: '追踪中', value: 0, color: '#f56c6c' },
  { label: '已找到', value: 0, color: '#67c23a' },
  { label: '累计失联', value: 0, color: '#e6a23c' },
])

const query = reactive({ status: '', person_id: null })
const form = reactive({
  person_id: null, lost_time: '', last_location: '',
  search_measures: '', family_contact: '', progress: '', status: 'tracking',
})
const rules = {
  person_id: [{ required: true, message: '请选择人员', trigger: 'change' }],
}

onMounted(async () => {
  const personRes = await getAllPersons()
  if (personRes.code === 200) personList.value = personRes.data
  fetchData()
  refreshStats()
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await listLostContactTracks({ ...query, page: page.value, per_page: perPage.value })
    if (res.code === 200) {
      tableData.value = res.data.items
      total.value = res.data.total
    }
  } finally { loading.value = false }
}

const refreshStats = async () => {
  const res = await listLostContactTracks({ per_page: 9999 })
  if (res.code === 200) {
    const items = res.data.items
    statCards.value[0].value = items.filter(i => i.status === 'tracking').length
    statCards.value[1].value = items.filter(i => i.status === 'resolved').length
    statCards.value[2].value = items.length
  }
}

const handleSearch = () => { page.value = 1; fetchData() }
const handleReset = () => {
  Object.assign(query, { status: '', person_id: null })
  page.value = 1; fetchData()
}

const openDialog = (row) => {
  editMode.value = !!row
  currentId.value = row ? row.track_id : null
  if (row) {
    Object.assign(form, {
      person_id: row.person_id, lost_time: toPicker(row.lost_time), last_location: row.last_location,
      search_measures: row.search_measures, family_contact: row.family_contact,
      progress: row.progress, status: row.status,
    })
  } else {
    Object.assign(form, {
      person_id: null, lost_time: '', last_location: '',
      search_measures: '', family_contact: '', progress: '', status: 'tracking',
    })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const res = editMode.value ? await updateLostContactTrack(currentId.value, form) : await createLostContactTrack(form)
    if (res.code === 200) { ElMessage.success('操作成功'); dialogVisible.value = false; fetchData(); refreshStats() }
  } finally { submitLoading.value = false }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该记录？', '提示')
    const res = await deleteLostContactTrack(row.track_id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchData(); refreshStats() }
  } catch {}
}

const handleResolve = async (row) => {
  try {
    await ElMessageBox.confirm(`确认人员 ${row.person_name} 已找到？`, '提示')
    const res = await updateLostContactTrack(row.track_id, { status: 'resolved' })
    if (res.code === 200) { ElMessage.success('已标记为已找到'); fetchData(); refreshStats() }
  } catch {}
}

const showDetail = (row) => {
  detailData.value = row
  detailVisible.value = true
}

function toPicker(dt) {
  return dt ? dt.replace('T', ' ').substring(0, 19) : ''
}
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 32px; font-weight: bold; }
.stat-label { margin-top: 6px; color: #909399; font-size: 14px; }
</style>
