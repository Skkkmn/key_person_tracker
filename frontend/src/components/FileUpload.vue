<template>
  <el-upload
    :action="uploadUrl"
    :headers="headers"
    :data="uploadData"
    :show-file-list="true"
    :on-success="handleSuccess"
    :on-error="handleError"
    :before-upload="beforeUpload"
    :file-list="fileList"
    list-type="picture-card"
    multiple
  >
    <el-icon><Plus /></el-icon>
  </el-upload>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const props = defineProps({
  entityType: { type: String, default: '' },
  entityId: { type: Number, default: null },
  fileList: { type: Array, default: () => [] },
})
const emit = defineEmits(['uploaded', 'error'])

const uploadUrl = computed(() => '/api/attachments/upload')
const headers = computed(() => ({ Authorization: `Bearer ${localStorage.getItem('token')}` }))
const uploadData = computed(() => ({ entity_type: props.entityType, entity_id: props.entityId }))

function beforeUpload(file) {
  const isImg = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp'].includes(file.type)
  const isDoc = ['application/pdf', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)
  if (!isImg && !isDoc) {
    ElMessage.error('仅支持图片和文档格式')
    return false
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  return true
}

function handleSuccess(res) {
  if (res.code === 200) {
    ElMessage.success('上传成功')
    emit('uploaded', res.data)
  } else {
    ElMessage.error(res.message || '上传失败')
    emit('error', res)
  }
}

function handleError(err) {
  ElMessage.error('上传失败')
  emit('error', err)
}
</script>
