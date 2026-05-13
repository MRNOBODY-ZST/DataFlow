<template>
  <div class="min-w-40 overflow-hidden rounded-xl bg-white shadow-md ring-1 ring-black/5 dark:bg-gray-800 dark:ring-white/10">
    <Handle type="target" :position="Position.Left" :style="handleStyle" />

    <!-- Colored header bar -->
    <div :class="['flex items-center gap-2 px-3 py-2 text-xs font-semibold text-white', headerBg]">
      <component :is="iconComponent" class="size-3.5" />
      <span>{{ schema?.label ?? type }}</span>
      <span v-if="data?.batch" class="ml-auto rounded bg-white/20 px-1.5 py-0.5 text-[10px] leading-none">BATCH</span>
    </div>

    <!-- Body -->
    <div class="px-3 py-2">
      <div v-if="summary" class="truncate text-[11px] text-gray-500 dark:text-gray-400">{{ summary }}</div>
      <div v-else class="text-[11px] text-gray-400 dark:text-gray-500 italic">No config</div>
    </div>

    <Handle type="source" :position="Position.Right" :style="handleStyle" />
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

const headerBg = computed(() => {
  const map: Record<string, string> = {
    readers: 'bg-blue-500',
    transforms: 'bg-amber-500',
    media: 'bg-purple-500',
    writers: 'bg-emerald-500',
  }
  return map[schema.value?.category || ''] || 'bg-gray-500'
})

const handleStyle = {
  width: '10px',
  height: '10px',
  background: '#6366f1',
  border: '2px solid white',
}

const summary = computed(() => {
  if (!props.data) return ''
  if (props.data.batch && props.data.prefix) return `batch: ${props.data.prefix}`
  return props.data.key || props.data.query || props.data.format || props.data.output_prefix || ''
})
</script>
