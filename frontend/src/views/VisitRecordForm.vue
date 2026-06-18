<template>
  <el-card>
    <template #header>
      <span style="font-weight:bold;font-size:16px">{{ isEdit ? '编辑走访记录' : '走访记录填报' }}</span>
    </template>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" v-loading="pageLoading">
      <el-divider content-position="left">任务信息</el-divider>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="关联人员" prop="person_id">
            <el-select v-model="form.person_id" placeholder="选择人员" filterable :disabled="!!taskId" style="width:100%">
              <el-option v-for="p in personList" :key="p.person_id" :label="`${p.name}(${p.id_card})`" :value="p.person_id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="走访任务">
            <el-select v-model="form.task_id" placeholder="关联任务（可选）" filterable clearable style="width:100%">
              <el-option v-for="t in taskList" :key="t.task_id" :label="t.title" :value="t.task_id" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">走访信息</el-divider>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="走访时间" prop="visit_time">
            <el-date-picker v-model="form.visit_time" type="datetime" style="width:100%" value-format="YYYY-MM-DD HH:mm:ss" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="走访地点" prop="location">
            <el-input v-model="form.location" placeholder="手动输入或获取定位">
              <template #append>
                <el-button @click="getLocation">定位</el-button>
              </template>
            </el-input>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="经度">
            <el-input v-model="form.longitude" placeholder="自动获取" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="纬度">
            <el-input v-model="form.latitude" placeholder="自动获取" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="表现情况">
            <el-select v-model="form.performance" clearable style="width:100%">
              <el-option label="良好" value="良好" />
              <el-option label="一般" value="一般" />
              <el-option label="较差" value="较差" />
              <el-option label="抗拒" value="抗拒" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">走访内容</el-divider>
      <el-form-item label="走访内容" prop="content">
        <el-input v-model="form.content" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="思想动态">
        <el-input v-model="form.thought_dynamics" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item label="生活困难">
        <el-input v-model="form.life_difficulty" type="textarea" :rows="2" />
      </el-form-item>

      <el-divider content-position="left">异常情况</el-divider>
      <el-form-item label="异常标记">
        <el-switch v-model="form.has_abnormality" active-text="存在异常" inactive-text="正常" />
      </el-form-item>
      <el-form-item v-if="form.has_abnormality" label="异常描述">
        <el-input v-model="form.abnormality_desc" type="textarea" :rows="2" placeholder="请描述异常情况" />
      </el-form-item>

      <el-divider content-position="left">佐证材料</el-divider>
      <el-form-item label="照片">
        <FileUpload v-model="form.photo_urls" />
      </el-form-item>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="录音">
            <el-input v-model="form.audio_url" placeholder="录音文件URL" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="录像">
            <el-input v-model="form.video_url" placeholder="录像文件URL" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <div style="text-align:center;margin-top:20px">
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" :loading="submitLoading" @click="handleSubmit">提交走访记录</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { listVisitRecords, createVisitRecord, updateVisitRecord, getVisitRecord } from '../api/visitRecord'
import { listVisitTasks } from '../api/visitTask'
import { getAllPersons } from '../api/keyPerson'
import FileUpload from '../components/FileUpload.vue'

const route = useRoute()
const router = useRouter()

const taskId = route.params?.taskId ? Number(route.params.taskId) : null
const recordId = route.params?.recordId ? Number(route.params.recordId) : null
const isEdit = !!recordId

const personList = ref([])
const taskList = ref([])
const pageLoading = ref(!!recordId)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  task_id: null, person_id: null, visit_time: nowStr(),
  location: '', longitude: '', latitude: '', content: '',
  performance: '', thought_dynamics: '', life_difficulty: '',
  has_abnormality: false, abnormality_desc: '',
  photo_urls: [], audio_url: '', video_url: '',
})

const rules = {
  person_id: [{ required: true, message: '请选择人员', trigger: 'change' }],
  visit_time: [{ required: true, message: '请选择走访时间', trigger: 'change' }],
  content: [{ required: true, message: '请输入走访内容', trigger: 'blur' }],
}

function nowStr() {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

onMounted(async () => {
  const [personRes, taskRes] = await Promise.all([getAllPersons(), listVisitTasks({ per_page: 200 })])
  if (personRes.code === 200) personList.value = personRes.data
  if (taskRes.code === 200) taskList.value = taskRes.data.items

  if (taskId) {
    form.task_id = taskId
    const found = taskList.value.find(t => t.task_id === taskId)
    if (found) form.person_id = found.person_id
  }
  function toPicker(dt) {
    return dt ? dt.replace('T', ' ').substring(0, 19) : ''
  }

  if (recordId) {
    const res = await getVisitRecord(recordId)
    if (res.code === 200) {
      const d = res.data
      Object.assign(form, {
        task_id: d.task_id, person_id: d.person_id, visit_time: toPicker(d.visit_time),
        location: d.location, longitude: d.longitude, latitude: d.latitude,
        content: d.content, performance: d.performance,
        thought_dynamics: d.thought_dynamics, life_difficulty: d.life_difficulty,
        has_abnormality: d.has_abnormality, abnormality_desc: d.abnormality_desc,
        photo_urls: d.photo_urls || [], audio_url: d.audio_url || '', video_url: d.video_url || '',
      })
    }
    pageLoading.value = false
  }
})

const getLocation = () => {
  if (!navigator.geolocation) { ElMessage.warning('浏览器不支持定位'); return }
  navigator.geolocation.getCurrentPosition(
    (pos) => { form.longitude = pos.coords.longitude.toFixed(7); form.latitude = pos.coords.latitude.toFixed(7); ElMessage.success('定位成功') },
    () => ElMessage.error('定位失败，请手动输入'),
  )
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const payload = {
      ...form,
      longitude: form.longitude ? Number(form.longitude) : null,
      latitude: form.latitude ? Number(form.latitude) : null,
      task_id: form.task_id || null,
    }
    const res = isEdit ? await updateVisitRecord(recordId, payload) : await createVisitRecord(payload)
    if (res.code === 200) {
      ElMessage.success(isEdit ? '更新成功' : '提交成功')
      router.push({ name: 'VisitTaskList' })
    }
  } finally { submitLoading.value = false }
}

const handleCancel = () => {
  router.push({ name: 'VisitTaskList' })
}
</script>
