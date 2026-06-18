<template>
  <div>
    <el-card>
      <div style="margin-bottom:16px">
        <el-button type="success" @click="openDialog()">新增标签</el-button>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="tag_name" label="标签名称" />
        <el-table-column label="颜色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :color="row.tag_color" style="color:#fff;border:none">{{ row.tag_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="70" align="center" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editMode ? '编辑标签' : '新增标签'" width="450px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="tag_name"><el-input v-model="form.tag_name" /></el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.tag_color" show-alpha />
          <span style="margin-left:8px;color:#909399">{{ form.tag_color }}</span>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
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
import { listTags, createTag, updateTag, deleteTag } from '../api/tag'

const tableData = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editMode = ref(false)
const currentId = ref(null)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({ tag_name: '', tag_color: '#409eff', sort_order: 0 })
const rules = { tag_name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }] }

const fetchData = async () => {
  loading.value = true
  try {
    const res = await listTags()
    if (res.code === 200) tableData.value = res.data
  } finally { loading.value = false }
}

onMounted(() => fetchData())

const openDialog = (row) => {
  editMode.value = !!row
  currentId.value = row ? row.tag_id : null
  if (row) Object.assign(form, { tag_name: row.tag_name, tag_color: row.tag_color, sort_order: row.sort_order })
  else Object.assign(form, { tag_name: '', tag_color: '#409eff', sort_order: 0 })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const res = editMode.value ? await updateTag(currentId.value, form) : await createTag(form)
    if (res.code === 200) { ElMessage.success('操作成功'); dialogVisible.value = false; fetchData() }
  } finally { submitLoading.value = false }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除标签 ${row.tag_name} ？`, '提示')
    const res = await deleteTag(row.tag_id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchData() }
  } catch {}
}
</script>
