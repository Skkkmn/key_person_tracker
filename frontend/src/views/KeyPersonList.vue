<template>
  <div>
    <el-card>
      <el-form :inline="true" :model="query" size="small">
        <el-form-item label="姓名"><el-input v-model="query.name" placeholder="姓名" clearable /></el-form-item>
        <el-form-item label="身份证"><el-input v-model="query.id_card" placeholder="身份证号" clearable /></el-form-item>
        <el-form-item label="人员类别">
          <el-select v-model="query.category_id" placeholder="全部" clearable style="width:140px">
            <el-option v-for="c in categories" :key="c.category_id" :label="c.category_name" :value="c.category_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="query.risk_level" placeholder="全部" clearable style="width:120px">
            <el-option label="高风险" value="high" /><el-option label="中风险" value="medium" /><el-option label="低风险" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="管控状态">
          <el-select v-model="query.control_status" placeholder="全部" clearable style="width:130px">
            <el-option label="管控中" value="monitored" /><el-option label="已撤销" value="removed" />
            <el-option label="已归档" value="archived" /><el-option label="失联" value="lost" /><el-option label="下落不明" value="missing" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="姓名/身份证/电话" clearable style="width:160px" />
        </el-form-item>
        <el-form-item label="标签">
          <div style="display:flex;gap:4px">
            <PersonTagSelect v-model="query.tag_ids" style="width:160px" />
            <el-select v-model="query.tag_mode" style="width:80px">
              <el-option label="或" value="or" />
              <el-option label="且" value="and" />
            </el-select>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button v-if="userStore.roleLevel >= 2" type="success" @click="openDialog()">新增人员</el-button>
          <el-dropdown v-if="userStore.roleLevel >= 2" style="margin-left:8px">
            <el-button type="warning">导入/导出<el-icon><ArrowDown /></el-icon></el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="exportData">导出Excel</el-dropdown-item>
                <el-dropdown-item @click="importVisible = true">导入Excel</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <el-table :data="tableData" border stripe v-loading="loading" @row-dblclick="handleRowClick">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="name" label="姓名" width="80" />
        <el-table-column prop="gender" label="性别" width="55" align="center">
          <template #default="{ row }">{{ row.gender === 'M' ? '男' : row.gender === 'F' ? '女' : '-' }}</template>
        </el-table-column>
        <el-table-column prop="id_card" label="身份证号" width="160" />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="category_name" label="类别" width="110" />
        <el-table-column prop="risk_level" label="风险" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="riskType(row.risk_level)" size="small">{{ riskLabel(row.risk_level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="control_status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.control_status)" size="small">{{ statusLabel(row.control_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="140">
          <template #default="{ row }">
            <el-tag v-for="t in (row.tags || [])" :key="t.tag_id" :color="t.tag_color" style="color:#fff;border:none;margin:1px" size="small">{{ t.tag_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department_name" label="管辖部门" width="100" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button v-if="userStore.roleLevel >= 2" size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button v-if="userStore.roleLevel >= 2" size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
            <el-dropdown trigger="click" @command="(cmd) => handleMore(cmd, row)">
              <el-button size="small" type="info" link>更多<el-icon><ArrowDown /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="userStore.roleLevel >= 2" command="archive" :disabled="row.control_status==='archived'">归档</el-dropdown-item>
                  <el-dropdown-item v-if="userStore.roleLevel >= 2" command="lost" :disabled="row.control_status==='lost'">标记失联</el-dropdown-item>
                  <el-dropdown-item command="cross_region">流入流出推送</el-dropdown-item>
                  <el-dropdown-item command="print">打印档案</el-dropdown-item>
                  <el-dropdown-item command="contact">联系人</el-dropdown-item>
                  <el-dropdown-item command="case">涉案信息</el-dropdown-item>
                  <el-dropdown-item command="track">活动轨迹</el-dropdown-item>
                  <el-dropdown-item command="alert">预警信息</el-dropdown-item>
                  <el-dropdown-item command="device_location" divided>定位设备</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:16px;text-align:right">
        <el-pagination v-model:current-page="page" v-model:page-size="perPage" :total="total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @size-change="fetchData" @current-change="fetchData" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editMode ? '编辑人员' : '新增人员'" width="800px">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="姓名" prop="name"><el-input v-model="form.name" /></el-form-item>
                <el-form-item label="身份证" prop="id_card"><el-input v-model="form.id_card" maxlength="18" /></el-form-item>
                <el-form-item label="性别">
                  <el-radio-group v-model="form.gender"><el-radio value="M">男</el-radio><el-radio value="F">女</el-radio></el-radio-group>
                </el-form-item>
                <el-form-item label="出生日期"><el-date-picker v-model="form.birth_date" type="date" style="width:100%" value-format="YYYY-MM-DD" /></el-form-item>
                <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
                <el-form-item label="学历">
                  <el-select v-model="form.education" clearable style="width:100%">
                    <el-option label="博士" value="博士" /><el-option label="硕士" value="硕士" />
                    <el-option label="本科" value="本科" /><el-option label="大专" value="大专" />
                    <el-option label="高中" value="高中" /><el-option label="初中" value="初中" /><el-option label="小学" value="小学" />
                  </el-select>
                </el-form-item>
                <el-form-item label="就业状况">
                  <el-select v-model="form.employment_status" clearable style="width:100%">
                    <el-option label="在职" value="在职" /><el-option label="待业" value="待业" />
                    <el-option label="退休" value="退休" /><el-option label="学生" value="学生" /><el-option label="无业" value="无业" />
                  </el-select>
                </el-form-item>
                <el-form-item label="工作单位"><el-input v-model="form.employer" /></el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="政治面貌">
                  <el-select v-model="form.political_status" clearable style="width:100%">
                    <el-option label="党员" value="党员" /><el-option label="团员" value="团员" /><el-option label="群众" value="群众" /><el-option label="其他" value="其他" />
                  </el-select>
                </el-form-item>
                <el-form-item label="民族"><el-input v-model="form.ethnicity" /></el-form-item>
                <el-form-item label="婚姻状况">
                  <el-select v-model="form.marital_status" clearable style="width:100%">
                    <el-option label="未婚" value="未婚" /><el-option label="已婚" value="已婚" />
                    <el-option label="离异" value="离异" /><el-option label="丧偶" value="丧偶" />
                  </el-select>
                </el-form-item>
                <el-form-item label="户籍类型">
                  <el-select v-model="form.household_type" clearable style="width:100%">
                    <el-option label="家庭户" value="家庭户" /><el-option label="集体户" value="集体户" />
                  </el-select>
                </el-form-item>
                <el-form-item label="人员类别">
                  <el-select v-model="form.category_id" placeholder="请选择" style="width:100%">
                    <el-option v-for="c in categories" :key="c.category_id" :label="c.category_name" :value="c.category_id" />
                  </el-select>
                </el-form-item>
                <el-form-item label="风险等级">
                  <el-select v-model="form.risk_level" style="width:100%">
                    <el-option label="高风险" value="high" /><el-option label="中风险" value="medium" /><el-option label="低风险" value="low" />
                  </el-select>
                </el-form-item>
                <el-form-item label="管辖部门">
                  <el-select v-model="form.department_id" placeholder="请选择" style="width:100%">
                    <el-option v-for="d in departments" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
                  </el-select>
                </el-form-item>
                <el-form-item label="管控状态">
                  <el-select v-model="form.control_status" style="width:100%">
                    <el-option label="管控中" value="monitored" /><el-option label="已撤销" value="removed" />
                    <el-option label="已归档" value="archived" /><el-option label="失联" value="lost" /><el-option label="下落不明" value="missing" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="户籍地址"><el-input v-model="form.address" type="textarea" :rows="2" /></el-form-item>
            <el-form-item label="现住地址"><el-input v-model="form.current_address" type="textarea" :rows="2" /></el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="扩展信息" name="ext">
          <el-form label-width="90px">
            <el-form-item label="标签">
              <PersonTagSelect v-model="form.tag_ids" />
            </el-form-item>
            <el-form-item label="主要事由">
              <el-input v-model="form.case_description" type="textarea" :rows="4" />
            </el-form-item>
            <el-form-item label="照片上传">
              <FileUpload entity-type="person" :entity-id="currentId" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="archiveVisible" title="人员归档" width="450px">
      <el-form ref="archiveFormRef" :model="archiveForm" label-width="80px">
        <el-form-item label="归档原因"><el-input v-model="archiveForm.reason" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="archiveVisible = false">取消</el-button>
        <el-button type="primary" :loading="archiveLoading" @click="handleArchive">确认归档</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="lostVisible" title="标记失联" width="450px">
      <el-form ref="lostFormRef" :model="lostForm" label-width="80px">
        <el-form-item label="失联详情"><el-input v-model="lostForm.lost_info" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="lostVisible = false">取消</el-button>
        <el-button type="primary" :loading="lostLoading" @click="handleMarkLost">确认标记</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importVisible" title="导入重点人员" width="500px">
      <el-upload :action="importUrl" :headers="importHeaders" :on-success="importSuccess" :on-error="importError" accept=".xlsx,.xls" :limit="1">
        <el-button type="primary">选择Excel文件</el-button>
        <template #tip><div style="color:#909399;font-size:12px;margin-top:4px">仅支持 .xlsx / .xls 格式</div></template>
      </el-upload>
      <template #footer>
        <el-button @click="importVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { listPersons, createPerson, updatePerson, deletePerson, archivePerson, markLost } from '../api/keyPerson'
import { listCategories } from '../api/personCategory'
import { listDepartments } from '../api/department'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store'
import PersonTagSelect from '../components/PersonTagSelect.vue'
import FileUpload from '../components/FileUpload.vue'
import { listTags } from '../api/tag'

const router = useRouter()
const userStore = useUserStore()

const categories = ref([])
const departments = ref([])
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
const activeTab = ref('basic')
const archiveVisible = ref(false)
const archiveLoading = ref(false)
const archiveFormRef = ref(null)
const archiveForm = reactive({ reason: '' })
const archivePersonId = ref(null)
const lostVisible = ref(false)
const lostLoading = ref(false)
const lostFormRef = ref(null)
const lostForm = reactive({ lost_info: '' })
const lostPersonId = ref(null)
const importVisible = ref(false)
const importUrl = '/api/import-export/import/persons'
const importHeaders = { Authorization: `Bearer ${localStorage.getItem('token')}` }

const query = reactive({
  name: '', id_card: '', category_id: null, risk_level: '', control_status: '', keyword: '',
  tag_ids: [], tag_mode: 'or',
})

const form = reactive({
  name: '', gender: 'M', id_card: '', birth_date: '', phone: '', address: '',
  current_address: '', photo_url: '', education: '', employment_status: '', employer: '',
  political_status: '', ethnicity: '', marital_status: '', household_type: '',
  category_id: null, risk_level: 'medium', department_id: null, control_status: 'monitored',
  case_description: '', tag_ids: [],
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  id_card: [{ required: true, message: '请输入身份证号', trigger: 'blur' }, { pattern: /^\d{17}[\dXx]$/, message: '身份证号格式不正确', trigger: 'blur' }],
}

onMounted(async () => {
  const [catRes, deptRes] = await Promise.all([listCategories({ status: 1 }), listDepartments({ status: 1 })])
  if (catRes.code === 200) categories.value = catRes.data
  if (deptRes.code === 200) departments.value = deptRes.data
  fetchData()
})

const fetchData = async () => {
  loading.value = true
  try {
    const params = { ...query, page: page.value, per_page: perPage.value }
    if (params.tag_ids && params.tag_ids.length) {
      params.tag_ids = params.tag_ids.join(',')
    } else {
      delete params.tag_ids
    }
    const res = await listPersons(params)
    if (res.code === 200) { tableData.value = res.data.items; total.value = res.data.total }
  } finally { loading.value = false }
}

const handleSearch = () => { page.value = 1; fetchData() }
const handleReset = () => {
  Object.assign(query, { name: '', id_card: '', category_id: null, risk_level: '', control_status: '', keyword: '', tag_ids: [], tag_mode: 'or' })
  page.value = 1; fetchData()
}

const openDialog = (row) => {
  editMode.value = !!row
  currentId.value = row ? row.person_id : null
  activeTab.value = 'basic'
  if (row) {
    Object.assign(form, {
      name: row.name, gender: row.gender, id_card: row.id_card, birth_date: row.birth_date,
      phone: row.phone, address: row.address, current_address: row.current_address,
      photo_url: row.photo_url, education: row.education || '', employment_status: row.employment_status || '',
      employer: row.employer || '', political_status: row.political_status || '',
      ethnicity: row.ethnicity || '', marital_status: row.marital_status || '',
      household_type: row.household_type || '',
      category_id: row.category_id, risk_level: row.risk_level,
      department_id: row.department_id, control_status: row.control_status,
      case_description: row.case_description || '',
      tag_ids: (row.tags || []).map(t => t.tag_id),
    })
  } else {
    Object.assign(form, {
      name: '', gender: 'M', id_card: '', birth_date: '', phone: '', address: '',
      current_address: '', photo_url: '', education: '', employment_status: '', employer: '',
      political_status: '', ethnicity: '', marital_status: '', household_type: '',
      category_id: null, risk_level: 'medium', department_id: null, control_status: 'monitored',
      case_description: '', tag_ids: [],
    })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const data = { ...form }
    const res = editMode.value ? await updatePerson(currentId.value, data) : await createPerson(data)
    if (res.code === 200) {
      ElMessage.success(editMode.value ? '更新成功' : '创建成功')
      dialogVisible.value = false; fetchData()
    }
  } finally { submitLoading.value = false }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除 ${row.name} ？`, '提示')
    const res = await deletePerson(row.person_id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchData() }
  } catch {}
}

const handleRowClick = (row) => openDialog(row)

const handleMore = (cmd, row) => {
  if (cmd === 'archive') {
    archivePersonId.value = row.person_id
    archiveForm.reason = ''
    archiveVisible.value = true
  } else if (cmd === 'lost') {
    lostPersonId.value = row.person_id
    lostForm.lost_info = ''
    lostVisible.value = true
  } else if (cmd === 'cross_region') {
    router.push({ name: 'CrossRegionTrackList', query: { person_id: row.person_id } })
  } else if (cmd === 'print') {
    const url = router.resolve({ name: 'PersonArchivePrint', params: { personId: row.person_id } })
    window.open(url.href, '_blank')
  } else if (cmd === 'device_location') {
    router.push({ name: 'MapView', query: { person_id: row.person_id } })
  } else {
    ElMessage.info(`查看 ${row.name} 的 ${cmd === 'contact' ? '联系人' : cmd === 'case' ? '涉案信息' : cmd === 'track' ? '活动轨迹' : '预警信息'}`)
  }
}

const handleArchive = async () => {
  archiveLoading.value = true
  try {
    const res = await archivePerson(archivePersonId.value, archiveForm.reason)
    if (res.code === 200) { ElMessage.success('归档成功'); archiveVisible.value = false; fetchData() }
  } finally { archiveLoading.value = false }
}

const handleMarkLost = async () => {
  lostLoading.value = true
  try {
    const res = await markLost(lostPersonId.value, lostForm.lost_info)
    if (res.code === 200) { ElMessage.success('已标记失联'); lostVisible.value = false; fetchData() }
  } finally { lostLoading.value = false }
}

const exportData = async () => {
  const token = localStorage.getItem('token')
  window.open(`/api/import-export/export/persons?token=${token}`, '_blank')
}

const importSuccess = (res) => {
  if (res.code === 200) { ElMessage.success(res.message); importVisible.value = false; fetchData() }
  else ElMessage.error(res.message || '导入失败')
}

const importError = () => { ElMessage.error('导入失败') }

const riskType = (v) => ({ high: 'danger', medium: 'warning', low: 'info' }[v] || 'info')
const riskLabel = (v) => ({ high: '高风险', medium: '中风险', low: '低风险' }[v] || v)
const statusType = (v) => ({ monitored: 'danger', removed: 'info', archived: 'success', lost: 'danger', missing: 'warning' }[v] || 'info')
const statusLabel = (v) => ({ monitored: '管控中', removed: '已撤销', archived: '已归档', lost: '失联', missing: '下落不明' }[v] || v)
</script>
