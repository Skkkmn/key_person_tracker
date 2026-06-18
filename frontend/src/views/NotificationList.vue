<template>
  <div>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color:#409eff">{{ total }}</div>
          <div class="stat-label">通知总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color:#e6a23c">{{ unreadCount }}</div>
          <div class="stat-label">未读通知</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <el-form :inline="true" :model="query" size="small">
          <el-form-item label="类型">
            <el-select v-model="query.notification_type" placeholder="全部" clearable style="width:110px">
              <el-option label="系统通知" value="system" />
              <el-option label="预警通知" value="alert" />
              <el-option label="任务通知" value="task" />
              <el-option label="评估通知" value="assessment" />
              <el-option label="流入流出" value="cross_region" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.is_read" placeholder="全部" clearable style="width:110px">
              <el-option label="未读" :value="0" />
              <el-option label="已读" :value="1" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="warning" :disabled="unreadCount === 0" @click="handleMarkAllRead">全部标为已读</el-button>
      </div>

      <el-table :data="tableData" border stripe v-loading="loading" @row-click="handleRowClick">
        <el-table-column width="40" align="center">
          <template #default="{ row }">
            <el-badge :hidden="row.is_read" is-dot />
          </template>
        </el-table-column>
        <el-table-column prop="notification_type" label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="typeTag(row.notification_type)" size="small">{{ typeLabel(row.notification_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span :style="{ fontWeight: row.is_read ? 'normal' : 'bold' }">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容" min-width="280" show-overflow-tooltip />
        <el-table-column prop="sender_name" label="发送人" width="80" />
        <el-table-column prop="created_at" label="时间" width="150" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click.stop="showDetail(row)">查看</el-button>
            <el-button v-if="!row.is_read" size="small" type="warning" link @click.stop="handleMarkRead(row)">标为已读</el-button>
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

    <el-drawer v-model="detailVisible" title="通知详情" size="450px">
      <template v-if="detailData">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="类型">
            <el-tag :type="typeTag(detailData.notification_type)" size="small">{{ typeLabel(detailData.notification_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="标题" content-style="font-weight:bold">{{ detailData.title }}</el-descriptions-item>
          <el-descriptions-item label="发送人">{{ detailData.sender_name || '系统' }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ detailData.created_at }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detailData.is_read ? 'info' : 'warning'" size="small">{{ detailData.is_read ? '已读' : '未读' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="detailData.entity_type" label="关联类型">{{ detailData.entity_type }}</el-descriptions-item>
          <el-descriptions-item label="内容" content-style="white-space:pre-wrap">{{ detailData.content || '-' }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listNotifications, getUnreadCount, markNotificationRead, markAllNotificationsRead } from '../api/notification'

const tableData = ref([])
const loading = ref(false)
const total = ref(0)
const unreadCount = ref(0)
const page = ref(1)
const perPage = ref(10)
const detailVisible = ref(false)
const detailData = ref(null)

const query = reactive({ notification_type: '', is_read: null })

onMounted(() => { fetchData(); refreshUnread() })

const fetchData = async () => {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (query.notification_type) params.notification_type = query.notification_type
    if (query.is_read !== null && query.is_read !== '') params.is_read = query.is_read
    const res = await listNotifications(params)
    if (res.code === 200) {
      tableData.value = res.data.items
      total.value = res.data.total
    }
  } finally { loading.value = false }
}

const refreshUnread = async () => {
  const res = await getUnreadCount()
  if (res.code === 200) unreadCount.value = res.data.count
}

const handleSearch = () => { page.value = 1; fetchData() }
const handleReset = () => {
  Object.assign(query, { notification_type: '', is_read: null })
  page.value = 1; fetchData()
}

const handleRowClick = (row) => {
  showDetail(row)
}

const showDetail = (row) => {
  detailData.value = row
  detailVisible.value = true
}

const handleMarkRead = async (row) => {
  const res = await markNotificationRead(row.notification_id)
  if (res.code === 200) {
    row.is_read = true
    refreshUnread()
    ElMessage.success('已标为已读')
  }
}

const handleMarkAllRead = async () => {
  try {
    await ElMessageBox.confirm('确认将所有通知标为已读？', '提示')
    const res = await markAllNotificationsRead()
    if (res.code === 200) { ElMessage.success('操作成功'); fetchData(); refreshUnread() }
  } catch {}
}

const typeTag = (v) => ({ system: 'info', alert: 'danger', task: 'warning', assessment: 'primary', cross_region: 'warning' }[v] || 'info')
const typeLabel = (v) => ({ system: '系统', alert: '预警', task: '任务', assessment: '评估', cross_region: '流入流出' }[v] || v)
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 32px; font-weight: bold; }
.stat-label { margin-top: 6px; color: #909399; font-size: 14px; }
</style>
