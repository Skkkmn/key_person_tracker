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
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <span style="font-weight:bold">人员风险评估</span>
        <div>
          <el-button type="primary" @click="handleBatchAssess">批量自动评估</el-button>
        </div>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="name" label="姓名" width="80" />
        <el-table-column prop="id_card" label="身份证号" width="180" />
        <el-table-column label="当前等级" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="riskTag(row.risk_level)" size="small">{{ riskLabel(row.risk_level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评估得分" width="80" align="center">
          <template #default="{ row }">
            <span :style="{ color: row._score >= 70 ? '#f56c6c' : row._score >= 40 ? '#e6a23c' : '#67c23a', fontWeight:'bold' }">{{ row._score ?? '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="评分详情" min-width="260">
          <template #default="{ row }">
            <el-tag v-for="(v,k) in row._details" :key="k" size="small" style="margin:2px">{{ k }}:{{ v }}</el-tag>
            <span v-if="!row._details" style="color:#999">未计算</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleCalculate(row)">评估</el-button>
            <el-button size="small" type="warning" link @click="openApplyDialog(row)">应用等级</el-button>
            <el-button size="small" type="info" link @click="handleHistory(row)">历史</el-button>
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

    <el-dialog v-model="applyVisible" title="应用风险评估等级" width="450px">
      <el-form :model="applyForm" label-width="90px">
        <el-form-item label="评估得分">
          <span style="font-size:24px;font-weight:bold;color:#409eff">{{ applyForm.score }}</span>
        </el-form-item>
        <el-form-item label="建议等级">
          <el-tag :type="riskTag(applyForm.suggested_level)" size="medium">{{ riskLabel(applyForm.suggested_level) }}</el-tag>
        </el-form-item>
        <el-form-item label="应用等级" prop="risk_level">
          <el-select v-model="applyForm.risk_level" style="width:100%">
            <el-option label="高风险" value="high" />
            <el-option label="中风险" value="medium" />
            <el-option label="低风险" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="原因说明">
          <el-input v-model="applyForm.reason" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="applyVisible = false">取消</el-button>
        <el-button type="primary" :loading="applyLoading" @click="handleApplySubmit">确认应用</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="historyVisible" title="风险评估历史" size="500px">
      <el-timeline v-if="historyData.length > 0">
        <el-timeline-item
          v-for="h in historyData"
          :key="h.assessment_id"
          :timestamp="h.created_at"
          placement="top"
        >
          <div>
            <el-tag :type="riskTag(h.previous_risk_level)" size="small">{{ riskLabel(h.previous_risk_level) }}</el-tag>
            <span style="margin:0 8px">→</span>
            <el-tag :type="riskTag(h.new_risk_level)" size="small">{{ riskLabel(h.new_risk_level) }}</el-tag>
            <span style="margin-left:8px;color:#909399">得分: {{ h.score }}</span>
          </div>
          <div style="margin-top:4px;color:#666;font-size:13px">
            <span>评估人: {{ h.assessor_name || '-' }}</span>
            <span v-if="h.reason" style="margin-left:12px">原因: {{ h.reason }}</span>
            <el-tag v-if="h.is_auto" size="small" type="info" style="margin-left:8px">自动</el-tag>
          </div>
          <div v-if="h.score_details" style="margin-top:4px">
            <el-tag v-for="(v,k) in h.score_details" :key="k" size="small" style="margin:2px">{{ k }}:{{ v }}</el-tag>
          </div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无评估历史" />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listPersons } from '../api/keyPerson'
import { calculateRisk, applyRiskAssessment, getRiskHistory, autoAssessAll } from '../api/riskAssessment'

const tableData = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const perPage = ref(10)
const applyVisible = ref(false)
const applyLoading = ref(false)
const applyPersonId = ref(null)
const historyVisible = ref(false)
const historyData = ref([])

const statCards = ref([
  { label: '高风险人员', value: 0, color: '#f56c6c' },
  { label: '中风险人员', value: 0, color: '#e6a23c' },
  { label: '低风险人员', value: 0, color: '#67c23a' },
])

const applyForm = reactive({ score: 0, suggested_level: 'low', risk_level: 'low', reason: '' })

onMounted(() => fetchData())

const fetchData = async () => {
  loading.value = true
  try {
    const res = await listPersons({ page: page.value, per_page: perPage.value })
    if (res.code === 200) {
      tableData.value = res.data.items.map(p => ({ ...p, _score: null, _details: null }))
      total.value = res.data.total
      refreshStats(res.data.items)
    }
  } finally { loading.value = false }
}

const refreshStats = (items) => {
  const high = items.filter(p => p.risk_level === 'high')
  const mid = items.filter(p => p.risk_level === 'medium')
  const low = items.filter(p => p.risk_level === 'low')
  statCards.value[0].value = high.length
  statCards.value[1].value = mid.length
  statCards.value[2].value = low.length
}

const handleCalculate = async (row) => {
  const res = await calculateRisk(row.person_id)
  if (res.code === 200) {
    row._score = res.data.score
    row._details = res.data.score_details
    ElMessage.success(`评估完成: ${res.data.score}分`)
  }
}

const openApplyDialog = async (row) => {
  if (!row._score) {
    const res = await calculateRisk(row.person_id)
    if (res.code !== 200) return
    row._score = res.data.score
    row._details = res.data.score_details
  }
  applyPersonId.value = row.person_id
  applyForm.score = row._score
  applyForm.suggested_level = row._score >= 70 ? 'high' : row._score >= 40 ? 'medium' : 'low'
  applyForm.risk_level = applyForm.suggested_level
  applyForm.reason = ''
  applyVisible.value = true
}

const handleApplySubmit = async () => {
  applyLoading.value = true
  try {
    const res = await applyRiskAssessment(applyPersonId.value, {
      risk_level: applyForm.risk_level, reason: applyForm.reason,
    })
    if (res.code === 200) { ElMessage.success('等级应用成功'); applyVisible.value = false; fetchData() }
  } finally { applyLoading.value = false }
}

const handleHistory = async (row) => {
  const res = await getRiskHistory(row.person_id)
  if (res.code === 200) {
    historyData.value = res.data
    historyVisible.value = true
  }
}

const handleBatchAssess = async () => {
  try {
    await ElMessageBox.confirm('将对所有人员进行批量自动风险评估，等级有变更的将自动更新，确认继续？', '提示')
    const res = await autoAssessAll()
    if (res.code === 200) { ElMessage.success(res.message); fetchData() }
  } catch {}
}

const riskTag = (v) => ({ high: 'danger', medium: 'warning', low: 'success' }[v] || 'info')
const riskLabel = (v) => ({ high: '高风险', medium: '中风险', low: '低风险' }[v] || v)
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 32px; font-weight: bold; }
.stat-label { margin-top: 6px; color: #909399; font-size: 14px; }
</style>
