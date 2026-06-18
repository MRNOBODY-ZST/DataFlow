<template>
  <div class="space-y-2">
    <!-- Summary of current mappings -->
    <div v-if="mappings.length > 0" class="space-y-1">
      <div
        v-for="(m, idx) in mappings.slice(0, 5)"
        :key="idx"
        class="flex items-center gap-1.5 rounded bg-gray-50 px-2 py-1 text-xs dark:bg-gray-700"
      >
        <span class="truncate font-mono text-blue-600 dark:text-blue-400">{{ m.source }}</span>
        <ArrowLongRightIcon class="size-3 shrink-0 text-gray-400" />
        <span class="truncate font-mono text-emerald-600 dark:text-emerald-400">{{ m.target }}</span>
      </div>
      <div v-if="mappings.length > 5" class="text-center text-[10px] text-gray-400">
        {{ t('jsonMapper.moreN', { n: mappings.length - 5 }) }}
      </div>
    </div>
    <div v-else class="rounded bg-gray-50 px-3 py-2 text-center text-xs text-gray-400 dark:bg-gray-700">
      {{ t('jsonMapper.noMapping') }}
    </div>

    <!-- Open mapper button -->
    <button
      type="button"
      class="w-full rounded-md bg-sky-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-sky-500 dark:bg-sky-500 dark:hover:bg-sky-400"
      @click="showMapper = true"
    >
      {{ t('jsonMapper.openMapper') }}
    </button>

    <JsonMapperModal
      :open="showMapper"
      :model-value="mappings"
      :sample="sample"
      :upstream-nodes="props.upstreamNodes"
      @update:model-value="onUpdate"
      @update:sample="$emit('update:sample', $event)"
      @close="showMapper = false"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowLongRightIcon } from '@heroicons/vue/24/outline'
import JsonMapperModal from './JsonMapperModal.vue'

import type { Node } from '@vue-flow/core'

interface MappingEntry {
  source: string
  target: string
  default?: string
}

const props = defineProps<{
  modelValue: MappingEntry[] | string | null
  sample?: string
  upstreamNodes?: Node[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: MappingEntry[]]
  'update:sample': [value: string]
}>()

const showMapper = ref(false)
const { t } = useI18n()

const mappings = computed<MappingEntry[]>(() => {
  if (!props.modelValue) return []
  if (typeof props.modelValue === 'string') {
    try {
      return JSON.parse(props.modelValue)
    } catch {
      return []
    }
  }
  return props.modelValue
})

function onUpdate(val: MappingEntry[]) {
  emit('update:modelValue', val)
}
</script>
