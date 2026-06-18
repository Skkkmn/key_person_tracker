<template>
  <div>
    <el-card>
      <div style="margin-bottom:16px">
        <el-button type="success" @click="openDialog()">新增部门</el-button>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading" row-key="dept_id" default-expand-all :tree-props="{ children: 'children' }">
        <el-table-column prop="dept_name" label="部门名称" />
        <el-table-column prop="dept_code" label="部门编码" width="150" />
        <el-table-column prop="address" label="地址" show-overflow-tooltip />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'info'" size="small">{{ row.status ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editMode ? '编辑部门' : '新增部门'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="部门名称" prop="dept_name"><el-input v-model="form.dept_name" /></el-form-item>
        <el-form-item label="部门编码" prop="dept_code"><el-input v-model="form.dept_code" /></el-form-item>
        <el-form-item label="上级部门">
          <el-tree-select v-model="form.parent_id" :data="treeData" :props="{ label: 'dept_name', value: 'dept_id' }" placeholder="无(顶级)" clearable style="width:100%" />
        </el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.phone" /></el-form-item>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createDepartment, updateDepartment, deleteDepartment, getDepartmentTree } from '../api/department'

const tableData = ref([])
const treeData = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editMode = ref(false)
const currentId = ref(null)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({ dept_name: '', dept_code: '', parent_id: null, address: '', phone: '', status: 1 })
const rules = {
  dept_name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  dept_code: [{ required: true, message: '请输入部门编码', trigger: 'blur' }],
}

const loadData = async () => {
  const res = await getDepartmentTree()
  if (res.code === 200) {
    tableData.value = res.data
    treeData.value = res.data
  }
}

onMounted(() => loadData())

const openDialog = (row) => {
  editMode.value = !!row
  currentId.value = row ? row.dept_id : null
  if (row) Object.assign(form, { dept_name: row.dept_name, dept_code: row.dept_code, parent_id: row.parent_id, address: row.address, phone: row.phone, status: row.status })
  else Object.assign(form, { dept_name: '', dept_code: '', parent_id: null, address: '', phone: '', status: 1 })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const res = editMode.value ? await updateDepartment(currentId.value, form) : await createDepartment(form)
    if (res.code === 200) { ElMessage.success('操作成功'); dialogVisible.value = false; loadData() }
  } finally { submitLoading.value = false }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除 ${row.dept_name} ？`, '提示')
    const res = await deleteDepartment(row.dept_id)
    if (res.code === 200) { ElMessage.success('删除成功'); loadData() }
  } catch {}
}
</script>
