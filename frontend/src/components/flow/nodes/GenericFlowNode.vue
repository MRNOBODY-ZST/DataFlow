<template>
  <div class="min-w-48 overflow-hidden rounded-xl bg-white shadow-md ring-1 ring-black/5 dark:bg-gray-800 dark:ring-white/10">
    <Handle type="target" :position="Position.Left" :style="handleStyle" />

    <!-- Colored header bar -->
    <div :class="['flex items-center gap-2 px-3 py-2 text-xs font-semibold text-white', headerBg]">
      <component :is="iconComponent" class="size-3.5" />
      <span>{{ schema?.label ?? type }}</span>
    </div>

    <!-- Inline fields -->
    <div v-if="inlineFields.length" class="space-y-2 px-3 py-2">
      <template v-for="field in inlineFields" :key="field.key">
        <div v-if="isFieldVisible(field)" class="space-y-0.5">
          <label v-if="field.type !== 'checkbox'" class="block text-[10px] font-medium text-gray-400 dark:text-gray-500">{{ field.label }}</label>

          <!-- Json mapper: compact preview -->
          <div v-if="field.widget === 'json-mapper'" class="space-y-0.5">
            <div v-if="mappingCount > 0" class="space-y-0.5">
              <div
                v-for="(m, idx) in mappingPreview"
                :key="idx"
                class="flex items-center gap-1 text-[10px]"
              >
                <span class="truncate font-mono text-blue-500">{{ m.source }}</span>
                <span class="shrink-0 text-gray-300">→</span>
                <span class="truncate font-mono text-emerald-500">{{ m.target }}</span>
              </div>
              <div v-if="mappingCount > 3" class="text-[9px] text-gray-400">+{{ mappingCount - 3 }} more</div>
            </div>
            <div v-else class="text-[10px] text-gray-400 italic">未配置映射</div>
          </div>

          <!-- Checkbox / toggle -->
          <div v-if="field.type === 'checkbox'" class="flex items-center gap-2">
            <button
              type="button"
              role="switch"
              :aria-checked="!!nodeData[field.key]"
              class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-sky-600 focus:ring-offset-1"
              :class="nodeData[field.key] ? 'bg-sky-600 dark:bg-sky-500' : 'bg-gray-200 dark:bg-gray-600'"
              @click.stop="updateField(field.key, !nodeData[field.key])"
            >
              <span
                class="pointer-events-none inline-block size-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                :class="nodeData[field.key] ? 'translate-x-4' : 'translate-x-0'"
              />
            </button>
            <span class="text-[11px] text-gray-600 dark:text-gray-400">{{ field.label }}</span>
          </div>

          <!-- Select -->
          <select
            v-else-if="field.type === 'select'"
            :value="nodeData[field.key] || ''"
            class="nodrag nowheel w-full rounded-md border-0 bg-gray-50 px-2 py-1 text-xs text-gray-700 ring-1 ring-gray-200 focus:ring-2 focus:ring-sky-500 dark:bg-gray-700 dark:text-gray-200 dark:ring-gray-600"
            @change.stop="updateField(field.key, ($event.target as HTMLSelectElement).value)"
          >
            <option v-for="option in field.options || []" :key="option" :value="option">{{ option }}</option>
          </select>

          <!-- Number -->
          <input
            v-else-if="field.type === 'number'"
            type="number"
            :value="nodeData[field.key] ?? ''"
            :placeholder="field.placeholder"
            class="nodrag nowheel w-full rounded-md border-0 bg-gray-50 px-2 py-1 text-xs text-gray-700 ring-1 ring-gray-200 focus:ring-2 focus:ring-sky-500 dark:bg-gray-700 dark:text-gray-200 dark:ring-gray-600"
            @change.stop="updateField(field.key, Number(($event.target as HTMLInputElement).value))"
          />

          <!-- File-picker: display only, click to open modal -->
          <div
            v-else-if="field.type === 'file-picker'"
            class="nodrag cursor-pointer truncate rounded-md bg-gray-50 px-2 py-1 text-xs text-gray-500 ring-1 ring-gray-200 hover:ring-sky-300 dark:bg-gray-700 dark:text-gray-400 dark:ring-gray-600 dark:hover:ring-sky-500"
            @dblclick.stop
          >
            {{ nodeData[field.key] || field.placeholder || 'Click to set' }}
          </div>

          <!-- Text (default) -->
          <input
            v-else
            type="text"
            :value="nodeData[field.key] || ''"
            :placeholder="field.placeholder"
            class="nodrag nowheel w-full rounded-md border-0 bg-gray-50 px-2 py-1 text-xs text-gray-700 ring-1 ring-gray-200 focus:ring-2 focus:ring-sky-500 dark:bg-gray-700 dark:text-gray-200 dark:ring-gray-600"
            @change.stop="updateField(field.key, ($event.target as HTMLInputElement).value)"
          />
        </div>
      </template>
    </div>

    <!-- Fallback: no inline fields configured -->
    <div v-else class="px-3 py-2">
      <div v-if="summary" class="truncate text-[11px] text-gray-500 dark:text-gray-400">{{ summary }}</div>
      <div v-else class="text-[11px] text-gray-400 dark:text-gray-500 italic">No config</div>
    </div>

    <Handle type="source" :position="Position.Right" :style="handleStyle" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position, useNode } from '@vue-flow/core'
import * as HeroIcons from '@heroicons/vue/24/outline'
import { useNodeSchemaStore } from '@/stores/nodeSchema'
import type { NodeFieldDef } from '@/stores/nodeSchema'

const props = defineProps<{
  type: string
  data?: Record<string, any>
}>()

const { node } = useNode()
const nodeSchemaStore = useNodeSchemaStore()
const schema = computed(() => nodeSchemaStore.byType[props.type])

const nodeData = computed(() => node.data ?? {})

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
    utils: 'bg-cyan-500',
  }
  return map[schema.value?.category || ''] || 'bg-gray-500'
})

const handleStyle = {
  width: '10px',
  height: '10px',
  background: '#0ea5e9',
  border: '2px solid white',
}

const inlineFields = computed(() => {
  return (schema.value?.fields ?? []).filter((f: NodeFieldDef) => f.inline)
})

const mappingPreview = computed(() => {
  const raw = nodeData.value.mappings
  if (!raw) return []
  const arr = typeof raw === 'string' ? (() => { try { return JSON.parse(raw) } catch { return [] } })() : raw
  return (arr as { source: string; target: string }[]).slice(0, 3)
})

const mappingCount = computed(() => {
  const raw = nodeData.value.mappings
  if (!raw) return 0
  const arr = typeof raw === 'string' ? (() => { try { return JSON.parse(raw) } catch { return [] } })() : raw
  return (arr as any[]).length
})

function isFieldVisible(_field: { key: string }) {
  return true
}

function updateField(key: string, value: any) {
  node.data = { ...node.data, [key]: value }
}

const summary = computed(() => {
  if (!props.data) return ''
  const val = props.data.key || props.data.query || props.data.format || props.data.output_prefix || ''
  if (typeof val === 'object' && val !== null) {
    const s = JSON.stringify(val)
    return s.length > 60 ? s.slice(0, 57) + '...' : s
  }
  return String(val)
})
</script>
