<template>
  <div :class="['rounded-lg border px-3 py-2 text-xs font-medium shadow-sm min-w-32 text-center', colorClass]">
    <Handle type="target" :position="Position.Left" />
    <component :is="iconComponent" class="mx-auto mb-1 size-5" />
    <div>{{ schema?.label ?? type }}</div>
    <div v-if="summary" class="mt-1 truncate text-[10px] opacity-75">{{ summary }}</div>
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import * as HeroIcons from '@heroicons/vue/24/outline'
import { useNodeSchemaStore } from '@/stores/nodeSchema'

const props = defineProps<{
  type: string
  data?: Record<string, any>
}>()

const nodeSchemaStore = useNodeSchemaStore()
const schema = computed(() => nodeSchemaStore.byType[props.type])

const iconComponent = computed(() => {
  const icons = HeroIcons as Record<string, any>
  return icons[schema.value?.icon || 'Square3Stack3DIcon'] ?? HeroIcons.Square3Stack3DIcon
})

const colorClass = computed(() => {
  const map: Record<string, string> = {
    readers: 'bg-blue-50 border-blue-200 text-blue-800',
    transforms: 'bg-amber-50 border-amber-200 text-amber-800',
    media: 'bg-purple-50 border-purple-200 text-purple-800',
    writers: 'bg-green-50 border-green-200 text-green-800',
  }
  return map[schema.value?.category || ''] || 'bg-gray-50 border-gray-200 text-gray-800'
})

const summary = computed(() => {
  if (!props.data) return ''
  return props.data.key || props.data.query || props.data.format || props.data.output_prefix || ''
})
</script>
