<template>
  <div>
    <el-card>
      <div style="margin-bottom:16px">
        <el-button v-if="isSuperAdmin" type="success" @click="openDialog()">新增用户</el-button>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="真实姓名" width="120" />
        <el-table-column prop="role" label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department_name" label="所属部门" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'info'" size="small">{{ row.status ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-if="isSuperAdmin" size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button v-if="isSuperAdmin" size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editMode ? '编辑用户' : '新增用户'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username"><el-input v-model="form.username" :disabled="editMode" /></el-form-item>
        <el-form-item label="密码" :prop="editMode ? '' : 'password'">
          <el-input v-model="form.password" type="password" show-password :placeholder="editMode ? '留空则不修改' : '请输入密码'" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name"><el-input v-model="form.real_name" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width:100%">
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="部门管理员" value="dept_admin" />
            <el-option label="操作员" value="operator" />
            <el-option label="查看员" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属部门">
          <el-select v-model="form.department_id" placeholder="请选择" clearable style="width:100%">
            <el-option v-for="d in departments" :key="d.dept_id" :label="d.dept_name" :value="d.dept_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.status" :active-value="1" :inactive-value="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listUsers, createUser, updateUser, deleteUser } from '../api/user'
import { listDepartments } from '../api/department'
import { useUserStore } from '../store'

const userStore = useUserStore()
const isSuperAdmin = computed(() => userStore.isSuperAdmin)

const tableData = ref([])
const departments = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editMode = ref(false)
const currentId = ref(null)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({ username: '', password: '', real_name: '', role: 'viewer', department_id: null, phone: '', status: 1 })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

onMounted(async () => {
  const deptRes = await listDepartments({ status: 1 })
  if (deptRes.code === 200) departments.value = deptRes.data
  fetchData()
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await listUsers()
    if (res.code === 200) tableData.value = res.data
  } finally { loading.value = false }
}

const openDialog = (row) => {
  editMode.value = !!row
  currentId.value = row ? row.user_id : null
  if (row) Object.assign(form, { username: row.username, password: '', real_name: row.real_name, role: row.role, department_id: row.department_id, phone: row.phone, status: row.status })
  else Object.assign(form, { username: '', password: '', real_name: '', role: 'operator', department_id: null, phone: '', status: 1 })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  if (editMode.value && !form.password) delete form.password
  submitLoading.value = true
  try {
    const res = editMode.value ? await updateUser(currentId.value, form) : await createUser(form)
    if (res.code === 200) { ElMessage.success('操作成功'); dialogVisible.value = false; fetchData() }
  } finally { submitLoading.value = false }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除用户 ${row.real_name} ？`, '提示')
    const res = await deleteUser(row.user_id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchData() }
  } catch {}
}

const roleLabel = (v) => ({
  super_admin: '超级管理员',
  dept_admin: '部门管理员',
  operator: '操作员',
  viewer: '查看员',
}[v] || v)
const roleTagType = (v) => ({
  super_admin: 'danger',
  dept_admin: 'warning',
  operator: 'primary',
  viewer: 'info',
}[v] || 'info')
</script>
