<template>
  <el-select v-model="selectedTags" multiple filterable collapse-tags collapse-tags-tooltip placeholder="选择标签" style="width:100%">
    <el-option v-for="t in tagList" :key="t.tag_id" :label="t.tag_name" :value="t.tag_id">
      <span>{{ t.tag_name }}</span>
      <el-tag :color="t.tag_color" style="margin-left:8px;width:12px;height:12px;border:none;display:inline-block;vertical-align:middle;border-radius:50%" />
    </el-option>
  </el-select>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { listTags } from '../api/tag'

const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])

const tagList = ref([])
const selectedTags = ref([...props.modelValue])

watch(selectedTags, (v) => emit('update:modelValue', v))
watch(() => props.modelValue, (v) => { selectedTags.value = [...v] })

onMounted(async () => {
  const res = await listTags()
  if (res.code === 200) tagList.value = res.data
})
</script>
