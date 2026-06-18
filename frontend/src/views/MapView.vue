<template>
  <div>
    <el-card>
      <el-form :inline="true" size="small">
        <el-form-item label="风险等级">
          <el-select v-model="filters.risk_level" clearable placeholder="全部" style="width:120px">
            <el-option label="高风险" value="high" /><el-option label="中风险" value="medium" /><el-option label="低风险" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="人员类别">
          <el-select v-model="filters.category_id" clearable placeholder="全部" style="width:140px">
            <el-option v-for="c in categories" :key="c.category_id" :label="c.category_name" :value="c.category_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="显示">
          <el-checkbox v-model="showPersonLabels">人员标签</el-checkbox>
          <el-checkbox v-model="showTrackLines">轨迹连线</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData" :loading="loading">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <PersonMap
        :points="mapPoints"
        :lines="trackLines"
        :point-size="showTrackLines ? 6 : 10"
        title="重点人员轨迹分布"
        @point-click="handlePointClick"
      />
    </el-card>

    <el-dialog v-model="detailVisible" :title="selectedPerson?.name || '轨迹详情'" width="600px">
      <template v-if="selectedPerson">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="姓名">{{ selectedPerson.name }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="riskType(selectedPerson.risk_level)" size="small">{{ riskLabel(selectedPerson.risk_level) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="人员类别">{{ selectedPerson.category_name }}</el-descriptions-item>
          <el-descriptions-item label="地址">{{ selectedPerson.current_address || selectedPerson.address }}</el-descriptions-item>
        </el-descriptions>
        <el-divider>活动轨迹</el-divider>
        <el-table :data="personTracks" v-loading="trackLoading" size="small" max-height="300">
          <el-table-column prop="track_time" label="时间" width="150" />
          <el-table-column prop="location" label="地点" />
          <el-table-column prop="activity_type" label="活动类型" width="100" />
        </el-table>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAllPersons } from '../api/keyPerson'
import { listCategories } from '../api/personCategory'
import { getGeoDistribution, getPersonTracks } from '../api/personTrack'
import PersonMap from '../components/PersonMap.vue'

const route = useRoute()
const categories = ref([])
const persons = ref([])
const tracks = ref([])
const detailVisible = ref(false)
const selectedPerson = ref(null)
const personTracks = ref([])
const trackLoading = ref(false)
const showPersonLabels = ref(true)
const showTrackLines = ref(false)
const loading = ref(false)
const filterPersonId = ref('')

const filters = reactive({ risk_level: '', category_id: '' })

onMounted(async () => {
  if (route.query.person_id) {
    filterPersonId.value = String(route.query.person_id)
  }
  try {
    const catRes = await listCategories({ status: 1 })
    if (catRes.code === 200) categories.value = catRes.data || []
  } catch { categories.value = [] }
  await loadData()
})

watch(() => route.query.person_id, (val) => {
  filterPersonId.value = val ? String(val) : ''
})

async function loadData() {
  loading.value = true
  try {
    const [personRes, trackRes] = await Promise.all([
      getAllPersons(),
      getGeoDistribution(),
    ])
    if (personRes && personRes.code === 200) {
      persons.value = Array.isArray(personRes.data) ? personRes.data : []
    }
    if (trackRes && trackRes.code === 200) {
      tracks.value = Array.isArray(trackRes.data) ? trackRes.data : []
    }
  } catch {
    persons.value = []
    tracks.value = []
  } finally {
    loading.value = false
  }
}

const personMap = computed(() => {
  const map = {}
  for (const p of persons.value) map[p.person_id] = p
  return map
})

const mapPoints = computed(() => {
  return tracks.value
    .filter(t => {
      const p = personMap.value[t.person_id]
      if (!p) return false
      if (filterPersonId.value && String(t.person_id) !== filterPersonId.value) return false
      if (filters.risk_level && p.risk_level !== filters.risk_level) return false
      if (filters.category_id && String(p.category_id) !== String(filters.category_id)) return false
      return true
    })
    .map(t => {
      const p = personMap.value[t.person_id]
      return {
        name: p?.name || '未知',
        longitude: t.longitude,
        latitude: t.latitude,
        risk_level: p?.risk_level,
        category_name: p?.category_name,
        address: p?.current_address || p?.address,
        person_id: t.person_id,
        track_time: t.track_time,
        location: t.location,
        activity_type: t.activity_type,
      }
    })
})

const trackLines = computed(() => {
  if (!showTrackLines.value) return []
  const groups = {}
  for (const t of tracks.value) {
    if (!t.longitude || !t.latitude) continue
    if (!groups[t.person_id]) groups[t.person_id] = []
    groups[t.person_id].push([t.longitude, t.latitude])
  }
  return Object.values(groups).map(coords => ({
    coords,
    lineStyle: { color: '#5470c6', width: 2, opacity: 0.4 },
  }))
})

async function handlePointClick(item) {
  const p = personMap.value[item.person_id]
  selectedPerson.value = p || { name: item.name }
  detailVisible.value = true
  trackLoading.value = true
  personTracks.value = []
  try {
    const res = await getPersonTracks(item.person_id)
    if (res && res.code === 200) {
      personTracks.value = Array.isArray(res.data) ? res.data : []
    }
  } catch {
    personTracks.value = []
  } finally {
    trackLoading.value = false
  }
}

const riskType = (v) => ({ high: 'danger', medium: 'warning', low: 'info' }[v] || 'info')
const riskLabel = (v) => ({ high: '高风险', medium: '中风险', low: '低风险' }[v] || v)
</script>
