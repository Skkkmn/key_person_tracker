<template>
  <div class="print-wrapper">
    <div class="no-print" style="text-align:center;padding:16px">
      <el-button type="primary" @click="windowPrint" size="large">打 印</el-button>
      <el-button @click="goBack" size="large">返回</el-button>
    </div>

    <div v-if="loading" class="no-print" style="text-align:center;padding:40px">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="person" id="print-area" class="print-area">
      <div class="archive-header">
        <h1>重点人员电子档案</h1>
        <div class="archive-meta">
          <span>档案编号：{{ person.id_card }}</span>
          <span>打印日期：{{ printDate }}</span>
        </div>
      </div>

      <section class="section">
        <h2 class="section-title">一、基本信息</h2>
        <table class="info-table">
          <tr><td class="label">姓名</td><td>{{ person.name }}</td><td class="label">性别</td><td>{{ genderLabel(person.gender) }}</td></tr>
          <tr><td class="label">身份证号</td><td>{{ person.id_card }}</td><td class="label">出生日期</td><td>{{ person.birth_date || '-' }}</td></tr>
          <tr><td class="label">手机号</td><td>{{ person.phone || '-' }}</td><td class="label">民族</td><td>{{ person.ethnicity || '-' }}</td></tr>
          <tr><td class="label">政治面貌</td><td>{{ person.political_status || '-' }}</td><td class="label">学历</td><td>{{ person.education || '-' }}</td></tr>
          <tr><td class="label">婚姻状况</td><td>{{ person.marital_status || '-' }}</td><td class="label">户籍类型</td><td>{{ person.household_type || '-' }}</td></tr>
          <tr><td class="label">就业状况</td><td>{{ person.employment_status || '-' }}</td><td class="label">工作单位</td><td>{{ person.employer || '-' }}</td></tr>
          <tr><td class="label">户籍地址</td><td colspan="3">{{ person.address || '-' }}</td></tr>
          <tr><td class="label">现住地址</td><td colspan="3">{{ person.current_address || '-' }}</td></tr>
          <tr><td class="label">人员类别</td><td>{{ person.category_name || '-' }}</td><td class="label">风险等级</td><td><span :class="'risk-tag risk-' + person.risk_level">{{ riskLabel(person.risk_level) }}</span></td></tr>
          <tr><td class="label">管控状态</td><td>{{ statusLabel(person.control_status) }}</td><td class="label">管辖部门</td><td>{{ person.department_name || '-' }}</td></tr>
          <tr><td class="label">标签</td><td colspan="3">{{ (person.tags || []).map(t => t.tag_name).join('、') || '-' }}</td></tr>
          <tr><td class="label">主要事由</td><td colspan="3">{{ person.case_description || '-' }}</td></tr>
          <tr><td class="label">创建人</td><td>{{ person.creator_name || '-' }}</td><td class="label">创建时间</td><td>{{ person.created_at || '-' }}</td></tr>
        </table>
      </section>

      <section class="section" v-if="archiveInfo">
        <h2 class="section-title">二、归档信息</h2>
        <table class="info-table">
          <tr><td class="label">归档时间</td><td>{{ person.archived_at || '-' }}</td><td class="label">归档人</td><td>{{ person.archiver_name || '-' }}</td></tr>
          <tr><td class="label">归档原因</td><td colspan="3">{{ person.archive_reason || '-' }}</td></tr>
        </table>
      </section>

      <section class="section" v-if="person.lost_at">
        <h2 class="section-title">{{ person.control_status === 'missing' ? '三、下落不明信息' : '三、失联信息' }}</h2>
        <table class="info-table">
          <tr><td class="label">失联时间</td><td>{{ person.lost_at || '-' }}</td><td class="label">失联详情</td><td>{{ person.lost_info || '-' }}</td></tr>
        </table>
      </section>

      <section class="section" v-if="contacts.length">
        <h2 class="section-title">四、联系人/家属</h2>
        <table class="data-table">
          <thead><tr><th>姓名</th><th>关系</th><th>联系电话</th><th>住址</th><th>紧急联系人</th></tr></thead>
          <tbody>
            <tr v-for="c in contacts" :key="c.contact_id">
              <td>{{ c.name }}</td><td>{{ c.relation || '-' }}</td><td>{{ c.phone || '-' }}</td>
              <td>{{ c.address || '-' }}</td><td>{{ c.is_emergency ? '是' : '否' }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="section" v-if="cases.length">
        <h2 class="section-title">五、涉案信息</h2>
        <table class="data-table">
          <thead><tr><th>案件名称</th><th>案件编号</th><th>案件类型</th><th>案发日期</th><th>案件状态</th></tr></thead>
          <tbody>
            <tr v-for="c in cases" :key="c.case_id">
              <td>{{ c.case_name }}</td><td>{{ c.case_number || '-' }}</td><td>{{ c.case_type || '-' }}</td>
              <td>{{ c.case_date || '-' }}</td><td>{{ c.case_status || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="section" v-if="tracks.length">
        <h2 class="section-title">六、活动轨迹</h2>
        <table class="data-table">
          <thead><tr><th>时间</th><th>地点</th><th>活动类型</th><th>来源</th></tr></thead>
          <tbody>
            <tr v-for="t in tracks" :key="t.track_id">
              <td>{{ t.track_time }}</td><td>{{ t.location }}</td><td>{{ t.activity_type || '-' }}</td><td>{{ t.source || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="section" v-if="alerts.length">
        <h2 class="section-title">七、预警信息</h2>
        <table class="data-table">
          <thead><tr><th>预警类型</th><th>预警内容</th><th>等级</th><th>时间</th><th>状态</th></tr></thead>
          <tbody>
            <tr v-for="a in alerts" :key="a.alert_id">
              <td>{{ a.alert_type }}</td><td>{{ a.alert_content }}</td><td>{{ alertLevelLabel(a.alert_level) }}</td>
              <td>{{ a.alert_time }}</td><td>{{ alertStatusLabel(a.status) }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="section" v-if="visitRecords.length">
        <h2 class="section-title">八、走访记录</h2>
        <table class="data-table">
          <thead><tr><th>走访时间</th><th>地点</th><th>走访人</th><th>表现</th><th>异常</th></tr></thead>
          <tbody>
            <tr v-for="r in visitRecords" :key="r.record_id">
              <td>{{ r.visit_time }}</td><td>{{ r.location || '-' }}</td><td>{{ r.visitor_name || '-' }}</td>
              <td>{{ r.performance || '-' }}</td><td>{{ r.has_abnormality ? '是' : '否' }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="section" v-if="riskAssessments.length">
        <h2 class="section-title">九、风险评估</h2>
        <table class="data-table">
          <thead><tr><th>评估时间</th><th>评估人</th><th>原风险</th><th>新风险</th><th>评分</th><th>原因</th></tr></thead>
          <tbody>
            <tr v-for="r in riskAssessments" :key="r.assessment_id">
              <td>{{ r.created_at }}</td><td>{{ r.assessor_name || '-' }}</td>
              <td>{{ riskLabel(r.previous_risk_level) }}</td><td>{{ riskLabel(r.new_risk_level) }}</td>
              <td>{{ r.score }}</td><td>{{ r.reason || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="section" v-if="lostContactTracks.length">
        <h2 class="section-title">十、失联追踪</h2>
        <table class="data-table">
          <thead><tr><th>失联时间</th><th>最后位置</th><th>状态</th><th>进展</th></tr></thead>
          <tbody>
            <tr v-for="l in lostContactTracks" :key="l.track_id">
              <td>{{ l.lost_time || '-' }}</td><td>{{ l.last_location || '-' }}</td>
              <td>{{ l.status === 'resolved' ? '已找到' : '追踪中' }}</td><td>{{ l.progress || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { getPersonArchive } from '../api/importExport'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const person = ref(null)
const contacts = ref([])
const cases = ref([])
const tracks = ref([])
const alerts = ref([])
const visitTasks = ref([])
const visitRecords = ref([])
const riskAssessments = ref([])
const lostContactTracks = ref([])

const printDate = new Date().toLocaleString('zh-CN')

const archiveInfo = computed(() => person.value?.archived_at)

onMounted(async () => {
  const personId = route.params.personId
  try {
    const res = await getPersonArchive(personId)
    if (res.code === 200) {
      const d = res.data
      person.value = d.person
      contacts.value = d.contacts
      cases.value = d.cases
      tracks.value = d.tracks
      alerts.value = d.alerts
      visitTasks.value = d.visit_tasks
      visitRecords.value = d.visit_records
      riskAssessments.value = d.risk_assessments
      lostContactTracks.value = d.lost_contact_tracks
    } else {
      ElMessage.error('加载档案失败')
    }
  } catch {
    ElMessage.error('加载档案失败')
  } finally {
    loading.value = false
  }
})

function windowPrint() {
  window.print()
}

function goBack() {
  router.back()
}

const genderLabel = (v) => ({ M: '男', F: '女' }[v] || '-')
const riskLabel = (v) => ({ high: '高风险', medium: '中风险', low: '低风险' }[v] || v || '-')
const statusLabel = (v) => ({ monitored: '管控中', removed: '已撤销', archived: '已归档', lost: '失联', missing: '下落不明' }[v] || v || '-')
const alertLevelLabel = (v) => ({ urgent: '紧急', important: '重要', normal: '普通' }[v] || v || '-')
const alertStatusLabel = (v) => ({ pending: '待处理', handled: '已处理', dismissed: '已忽略' }[v] || v || '-')
</script>

<style>
@media print {
  .no-print { display: none !important; }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .print-area { margin: 0; padding: 0; }
  .section { page-break-inside: avoid; }
}

body {
  margin: 0;
  font-family: 'SimSun', '宋体', serif;
  font-size: 14px;
  color: #333;
}

.print-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.print-area {
  background: #fff;
  padding: 40px;
}

.archive-header {
  text-align: center;
  border-bottom: 2px solid #333;
  padding-bottom: 20px;
  margin-bottom: 30px;
}

.archive-header h1 {
  font-size: 24px;
  margin: 0 0 10px 0;
  letter-spacing: 4px;
}

.archive-meta {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #666;
}

.section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 16px;
  border-left: 4px solid #409eff;
  padding-left: 10px;
  margin: 0 0 12px 0;
  color: #222;
}

.info-table {
  width: 100%;
  border-collapse: collapse;
}

.info-table td {
  border: 1px solid #999;
  padding: 6px 10px;
  font-size: 13px;
}

.info-table .label {
  width: 100px;
  background: #f5f7fa;
  font-weight: bold;
  text-align: center;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f0f2f5;
  border: 1px solid #999;
  padding: 6px 8px;
  font-size: 13px;
  text-align: center;
}

.data-table td {
  border: 1px solid #999;
  padding: 5px 8px;
  font-size: 13px;
}

.risk-tag {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 2px;
  font-size: 12px;
  color: #fff;
}

.risk-high { background: #f56c6c; }
.risk-medium { background: #e6a23c; }
.risk-low { background: #67c23a; }
</style>
