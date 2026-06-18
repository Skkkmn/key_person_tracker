<template>
  <div>
    <el-card>
      <div style="margin-bottom:16px">
        <el-button type="success" @click="openDialog()">新增类别</el-button>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="category_name" label="类别名称" />
        <el-table-column prop="category_code" label="类别编码" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
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

    <el-dialog v-model="dialogVisible" :title="editMode ? '编辑类别' : '新增类别'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="类别名称" prop="category_name"><el-input v-model="form.category_name" /></el-form-item>
        <el-form-item label="类别编码" prop="category_code"><el-input v-model="form.category_code" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
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
import { listCategories, createCategory, updateCategory, deleteCategory } from '../api/personCategory'

const tableData = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editMode = ref(false)
const currentId = ref(null)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({ category_name: '', category_code: '', description: '', sort_order: 0, status: 1 })
const rules = {
  category_name: [{ required: true, message: '请输入类别名称', trigger: 'blur' }],
  category_code: [{ required: true, message: '请输入类别编码', trigger: 'blur' }],
}

onMounted(() => fetchData())

const fetchData = async () => {
  loading.value = true
  try {
    const res = await listCategories()
    if (res.code === 200) tableData.value = res.data
  } finally { loading.value = false }
}

const openDialog = (row) => {
  editMode.value = !!row
  currentId.value = row ? row.category_id : null
  if (row) Object.assign(form, { category_name: row.category_name, category_code: row.category_code, description: row.description, sort_order: row.sort_order, status: row.status })
  else Object.assign(form, { category_name: '', category_code: '', description: '', sort_order: 0, status: 1 })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const res = editMode.value ? await updateCategory(currentId.value, form) : await createCategory(form)
    if (res.code === 200) { ElMessage.success('操作成功'); dialogVisible.value = false; fetchData() }
  } finally { submitLoading.value = false }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除 ${row.category_name} ？`, '提示')
    const res = await deleteCategory(row.category_id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchData() }
  } catch {}
}
</script>
