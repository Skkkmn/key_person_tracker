<template>
  <div>
    <el-card>
      <el-form :inline="true" :model="query" size="small">
        <el-form-item label="操作类型">
          <el-select v-model="query.action" placeholder="全部" clearable style="width:140px">
            <el-option label="新增" value="CREATE" />
            <el-option label="修改" value="UPDATE" />
            <el-option label="删除" value="DELETE" />
            <el-option label="归档" value="ARCHIVE" />
            <el-option label="失联标记" value="MARK_LOST" />
            <el-option label="状态变更" value="STATUS_CHANGE" />
            <el-option label="导出" value="EXPORT" />
            <el-option label="导入" value="IMPORT" />
            <el-option label="登录" value="LOGIN" />
            <el-option label="修改密码" value="CHANGE_PASSWORD" />
            <el-option label="上传" value="UPLOAD" />
            <el-option label="设置标签" value="SET_TAGS" />
            <el-option label="应用评估" value="APPLY_RISK" />
            <el-option label="自动评估" value="AUTO_ASSESS" />
            <el-option label="处理预警" value="HANDLE" />
            <el-option label="自动生成" value="AUTO_GENERATE" />
          </el-select>
        </el-form-item>
        <el-form-item label="对象类型">
          <el-select v-model="query.entity_type" placeholder="全部" clearable style="width:140px">
            <el-option label="重点人员" value="key_person" />
            <el-option label="走访任务" value="visit_task" />
            <el-option label="走访记录" value="visit_record" />
            <el-option label="风险评估" value="risk_assessment" />
            <el-option label="预警" value="alert" />
            <el-option label="人员预警" value="person_alert" />
            <el-option label="失联追踪" value="lost_contact" />
            <el-option label="用户" value="user" />
            <el-option label="部门" value="department" />
            <el-option label="人员类别" value="person_category" />
            <el-option label="标签" value="tag" />
            <el-option label="附件" value="attachment" />
            <el-option label="轨迹" value="person_track" />
            <el-option label="案件" value="person_case" />
            <el-option label="联系人" value="person_contact" />
            <el-option label="认证" value="auth" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作人">
          <el-input v-model="query.username" placeholder="用户名" clearable style="width:120px" />
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker v-model="query.start_time" type="datetime" placeholder="开始" value-format="YYYY-MM-DD HH:mm:ss" style="width:150px" />
          <span style="margin:0 6px">~</span>
          <el-date-picker v-model="query.end_time" type="datetime" placeholder="结束" value-format="YYYY-MM-DD HH:mm:ss" style="width:150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="created_at" label="操作时间" width="160" />
        <el-table-column prop="username" label="操作人" width="90" />
        <el-table-column label="操作类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="actionType(row.action)" size="small">{{ actionLabel(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="对象类型" width="95">
          <template #default="{ row }">
            {{ typeLabel(row.entity_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="entity_name" label="对象名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="变更内容" min-width="200">
          <template #default="{ row }">
            <template v-if="row.old_value">
              <el-tag size="small" type="danger" style="margin:2px" v-for="(v, k) in row.old_value" :key="'o'+k">
                {{ k }}: {{ v }}
              </el-tag>
              <span style="margin:0 4px;color:#909399">→</span>
            </template>
            <template v-if="row.new_value">
              <el-tag size="small" type="success" style="margin:2px" v-for="(v, k) in row.new_value" :key="'n'+k">
                {{ typeof v === 'object' ? JSON.stringify(v) : v }}
              </el-tag>
            </template>
            <span v-if="!row.old_value && !row.new_value && row.action === 'CREATE'" style="color:#67c23a">新建记录</span>
            <span v-if="!row.old_value && !row.new_value && row.action === 'DELETE'" style="color:#f56c6c">删除记录</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="130" />
      </el-table>
      <div style="margin-top:16px;text-align:right">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="perPage"
          :total="total"
          :page-sizes="[10,20,50,100]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { listLogs } from '../api/operationLog'

const tableData = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const perPage = ref(20)

const query = reactive({ action: '', entity_type: '', username: '', start_time: '', end_time: '' })

const actionMap = {
  CREATE: { label: '新增', type: 'success' },
  UPDATE: { label: '修改', type: 'warning' },
  DELETE: { label: '删除', type: 'danger' },
  ARCHIVE: { label: '归档', type: 'info' },
  MARK_LOST: { label: '失联', type: 'danger' },
  STATUS_CHANGE: { label: '状态变更', type: 'warning' },
  EXPORT: { label: '导出', type: 'primary' },
  IMPORT: { label: '导入', type: 'success' },
  LOGIN: { label: '登录', type: 'primary' },
  CHANGE_PASSWORD: { label: '修改密码', type: 'warning' },
  UPLOAD: { label: '上传', type: 'primary' },
  SET_TAGS: { label: '设置标签', type: 'warning' },
  APPLY_RISK: { label: '应用评估', type: 'warning' },
  AUTO_ASSESS: { label: '自动评估', type: 'info' },
  HANDLE: { label: '处理', type: 'success' },
  AUTO_GENERATE: { label: '自动生成', type: 'info' },
  VERIFY: { label: '核实', type: 'primary' },
  REVIEW: { label: '审核', type: 'warning' },
}
const actionLabel = (v) => actionMap[v]?.label || v
const actionType = (v) => actionMap[v]?.type || 'info'
const typeLabel = (v) => ({
  key_person: '重点人员', person_alert: '人员预警', alert: '预警',
  visit_task: '走访任务', visit_record: '走访记录',
  risk_assessment: '风险评估', lost_contact: '失联追踪',
  user: '用户', department: '部门',
  person_category: '人员类别', tag: '标签',
  attachment: '附件', person_track: '轨迹',
  person_case: '案件', person_contact: '联系人',
  auth: '认证',
}[v] || v)

const fetchData = async () => {
  loading.value = true
  try {
    const res = await listLogs({ ...query, page: page.value, per_page: perPage.value })
    if (res.code === 200) {
      tableData.value = res.data.items
      total.value = res.data.total
    }
  } finally { loading.value = false }
}

onMounted(() => fetchData())

const handleSearch = () => { page.value = 1; fetchData() }
const handleReset = () => {
  Object.assign(query, { action: '', entity_type: '', username: '', start_time: '', end_time: '' })
  page.value = 1
  fetchData()
}
</script>
