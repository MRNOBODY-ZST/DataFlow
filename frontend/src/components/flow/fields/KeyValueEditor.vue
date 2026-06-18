<template>
  <div class="space-y-2">
    <div v-for="(entry, index) in entries" :key="index" class="flex gap-2">
    <input
        v-model="entries[index].key"
        type="text"
        :placeholder="keyPlaceholder"
        class="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
        @input="emitChange"
      />
      <span class="flex items-center text-gray-400">→</span>
      <input
        v-if="valueType === 'text'"
        v-model="entries[index].value"
      type="text"
        :placeholder="valuePlaceholder"
        class="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
        @input="emitChange"
      />
      <select
        v-else-if="valueType === 'select'"
        v-model="entries[index].value"
        class="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
        @change="emitChange"
      >
        <option value="">选择...</option>
        <option v-for="opt in valueOptions" :key="opt" :value="opt">{{ opt }}</option>
      </select>
      <button
        type="button"
        class="rounded-md bg-red-50 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-100"
        @click="removeEntry(index)"
      >
        删除
      </button>
    </div>
    <button
      type="button"
      class="w-full rounded-md border border-dashed border-gray-300 px-3 py-2 text-sm font-medium text-gray-600 hover:border-gray-400 hover:bg-gray-50"
      @click="addEntry"
    >
      + 添加映射
    </button>
    <div class="flex items-center gap-2">
      <button
        type="button"
        class="text-xs text-gray-500 hover:text-gray-700"
        @click="showManual = !showManual"
      >
        {{ showManual ? '隐藏' : '显示' }}手动编辑
      </button>
    </div>
    <textarea
      v-if="showManual"
      v-model="manualValue"
      rows="4"
      placeholder='{"key1": "value1", "key2": "value2"}'
      class="w-full rounded-md border border-gray-300 px-3 py-2 font-mono text-xs focus:border-sky-500 focus:outline-none"
      @input="onManualChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: Record<string, string> | string | null
  keyPlaceholder?: string
  valuePlaceholder?: string
  valueType?: 'text' | 'select'
  valueOptions?: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, string>]
}>()

interface Entry {
  key: string
  value: string
}

const entries = ref<Entry[]>([])
const showManual = ref(false)
const manualValue = ref('')

function parseValue(value: Record<string, string> | string | null): Entry[] {
  let obj: Record<string, string> = {}

  if (value && typeof value === 'object' && !Array.isArray(value)) {
    obj = value
  } else if (typeof value === 'string' && value.trim()) {
    try {
      const parsed = JSON.parse(value)
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        obj = parsed
      }
    } catch {
      // Invalid JSON
    }
  }

  return Object.entries(obj).map(([key, value]) => ({ key, value }))
}

watch(
  () => props.modelValue,
  (newValue) => {
    entries.value = parseValue(newValue)
    const obj = Object.fromEntries(entries.value.map((e) => [e.key, e.value]))
    manualValue.value = JSON.stringify(obj, null, 2)
  },
  { immediate: true },
)

function addEntry() {
  entries.value.push({ key: '', value: '' })
  emitChange()
}

function removeEntry(index: number) {
  entries.value.splice(index, 1)
  emitChange()
}

function emitChange() {
  const obj = Object.fromEntries(
    entries.value.filter((e) => e.key.trim()).map((e) => [e.key, e.value]),
  )
  emit('update:modelValue', obj)
  manualValue.value = JSON.stringify(obj, null, 2)
}

function onManualChange() {
  try {
    const parsed = JSON.parse(manualValue.value)
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      entries.value = Object.entries(parsed).map(([key, value]) => ({
        key,
        value: String(value),
      }))
      emit('update:modelValue', parsed)
    }
  } catch {
    // Invalid JSON, ignore
  }
}
</script>
