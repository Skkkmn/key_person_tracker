<template>
  <div style="position:relative;min-height:200px">
    <div v-if="!mapLoaded && !mapError" style="height:500px;display:flex;align-items:center;justify-content:center;color:#999">
      正在加载地图数据...
    </div>
    <div v-else-if="mapError" style="height:500px;display:flex;align-items:center;justify-content:center;color:#f56c6c">
      地图加载失败，请检查网络连接后刷新
    </div>
    <v-chart v-else :option="option" style="height:500px" @click="handleChartClick" autoresize />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { MapChart, ScatterChart, EffectScatterChart, LinesChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, VisualMapComponent, LegendComponent } from 'echarts/components'
import * as echarts from 'echarts/core'
import VChart from 'vue-echarts'

use([CanvasRenderer, MapChart, ScatterChart, EffectScatterChart, LinesChart, TitleComponent, TooltipComponent, VisualMapComponent, LegendComponent])

const props = defineProps({
  points: { type: Array, default: () => [] },
  lines: { type: Array, default: () => [] },
  mapUrl: { type: String, default: '' },
  title: { type: String, default: '' },
  pointSize: { type: Number, default: 8 },
})

const emit = defineEmits(['pointClick'])

const mapName = ref('china')
const mapLoaded = ref(false)
const mapError = ref(false)

async function loadMap() {
  mapLoaded.value = false
  mapError.value = false
  let url = props.mapUrl
  if (!url) {
    url = 'https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json'
  }
  try {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 15000)
    const res = await fetch(url, { signal: controller.signal })
    clearTimeout(timeout)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const geoJson = await res.json()
    echarts.registerMap(mapName.value, geoJson)
    mapLoaded.value = true
  } catch (e) {
    mapError.value = true
  }
}

onMounted(loadMap)

const scatterData = computed(() =>
  props.points.filter(p => p.longitude != null && p.latitude != null).map(p => ({
    value: [p.longitude, p.latitude],
    name: p.name || p.location || '',
    person_id: p.person_id,
    risk_level: p.risk_level,
  }))
)

const lineData = computed(() => {
  if (!props.lines || !props.lines.length) return []
  return props.lines.map(group => ({
    coords: group.coords,
    lineStyle: group.lineStyle || { color: '#5470c6', width: 2, opacity: 0.4 },
  }))
})

const option = computed(() => ({
  title: { text: props.title, left: 'center', textStyle: { fontSize: 16 } },
  tooltip: {
    trigger: 'item',
    formatter: (p) => {
      if (p.componentType === 'series') {
        return `${p.name}<br/>经度: ${p.value[0]}<br/>纬度: ${p.value[1]}`
      }
      return ''
    },
  },
  visualMap: {
    min: 0, max: 100, text: ['多', '少'],
    left: 'left', top: 'bottom',
    inRange: { color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695'] },
    show: false,
  },
  series: [
    {
      type: 'map',
      map: mapName.value,
      roam: true,
      label: { show: false },
      itemStyle: { areaColor: '#f3f3f3', borderColor: '#999' },
      emphasis: { label: { show: true }, itemStyle: { areaColor: '#e6e6e6' } },
      selectedMode: false,
    },
    ...(lineData.value.length ? [{
      type: 'lines',
      data: lineData.value,
      polyline: true,
      effect: { show: true, period: 6, trailLength: 0, symbol: 'arrow', symbolSize: 6 },
      lineStyle: { width: 2, opacity: 0.6, curveness: 0.2 },
    }] : []),
    {
      type: 'effectScatter',
      coordinateSystem: 'geo',
      data: scatterData.value,
      symbolSize: props.pointSize,
      label: { show: true, formatter: (p) => p.name, position: 'right', fontSize: 10 },
      itemStyle: {
        color: (p) => {
          const colors = { high: '#f56c6c', medium: '#e6a23c', low: '#67c23a' }
          return colors[p.data?.risk_level] || '#409eff'
        },
      },
      emphasis: { scale: 1.5 },
    },
  ],
}))

function handleChartClick(params) {
  if (params.componentType === 'series' && params.seriesType === 'effectScatter') {
    const item = props.points.find(p => String(p.person_id) === String(params.data?.person_id))
    if (item) emit('pointClick', item)
  }
}
</script>
