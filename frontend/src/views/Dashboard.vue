<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="6" v-for="item in statCards" :key="item.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card>
          <template #header>人员类别分布</template>
          <v-chart :option="categoryOption" style="height:300px" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>风险等级分布</template>
          <v-chart :option="riskOption" style="height:300px" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent } from 'echarts/components'
use([CanvasRenderer, PieChart, TitleComponent, TooltipComponent])
import { getPersonStats } from '../api/keyPerson'
import { listCategories } from '../api/personCategory'

const statCards = ref([
  { label: '重点人员总数', value: 0 },
  { label: '高风险人员', value: 0 },
  { label: '中风险人员', value: 0 },
  { label: '低风险人员', value: 0 },
])

const categories = ref([])
const stats = ref(null)

onMounted(async () => {
  const [catRes, statRes] = await Promise.all([
    listCategories({ status: 1 }),
    getPersonStats(),
  ])
  if (catRes.code === 200) categories.value = catRes.data
  if (statRes.code === 200) {
    stats.value = statRes.data
    statCards.value[0].value = statRes.data.total || 0
    statCards.value[1].value = statRes.data.by_risk?.high || 0
    statCards.value[2].value = statRes.data.by_risk?.medium || 0
    statCards.value[3].value = statRes.data.by_risk?.low || 0
  }
})

const categoryMap = computed(() => {
  const m = {}
  categories.value.forEach((c) => { m[c.category_id] = c.category_name })
  return m
})

const categoryChartData = computed(() => {
  if (!stats.value?.by_category) return []
  return Object.entries(stats.value.by_category).map(([k, v]) => ({
    name: categoryMap.value[k] || `类别${k}`,
    value: v,
  }))
})

const categoryOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: categoryChartData.value,
    label: { show: true, formatter: '{b}: {c}' },
  }],
}))

const riskChartData = computed(() => {
  if (!stats.value?.by_risk) return []
  const map = { high: '高风险', medium: '中风险', low: '低风险' }
  return Object.entries(stats.value.by_risk).map(([k, v]) => ({
    name: map[k] || k,
    value: v,
  }))
})

const riskOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: riskChartData.value,
    label: { show: true, formatter: '{b}: {c}' },
  }],
}))
</script>

<style scoped>
.stat-card {
  text-align: center;
}
.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
}
.stat-label {
  margin-top: 8px;
  color: #909399;
  font-size: 14px;
}
</style>
