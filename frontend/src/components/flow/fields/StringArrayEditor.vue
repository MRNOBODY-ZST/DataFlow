<template>
  <div class="space-y-2">
    <div v-for="(item, index) in items" :key="index" class="flex gap-2">
      <input
        v-model="items[index]"
        type="text"
        :placeholder="placeholder"
        class="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
        @input="emitChange"
      />
      <button
        type="button"
        class="rounded-md bg-red-50 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-100"
        @click="removeItem(index)"
      >
      删除
      </button>
    </div>
    <button
      type="button"
      class="w-full rounded-md border border-dashed border-gray-300 px-3 py-2 text-sm font-medium text-gray-600 hover:border-gray-400 hover:bg-gray-50"
      @click="addItem"
    >
      + 添加项
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
      rows="3"
      placeholder='["item1", "item2"]'
      class="w-full rounded-md border border-gray-300 px-3 py-2 font-mono text-xs focus:border-indigo-500 focus:outline-none"
      @input="onManualChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: string[] | string | null
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const items = ref<string[]>([])
const showManual = ref(false)
const manualValue = ref('')

function parseValue(value: string[] | string | null): string[] {
  if (Array.isArray(value)) return value
  if (typeof value === 'string' && value.trim()) {
    try {
      const parsed = JSON.parse(value)
      return Array.isArray(parsed) ? parsed : []
    } catch {
      return []
    }
  }
  return []
}

watch(
  () => props.modelValue,
  (newValue) => {
    items.value = parseValue(newValue)
    manualValue.value = JSON.stringify(items.value, null, 2)
  },
  { immediate: true },
)

function addItem() {
  items.value.push('')
  emitChange()
}

function removeItem(index: number) {
  items.value.splice(index, 1)
  emitChange()
}

function emitChange() {
  emit('update:modelValue', items.value)
  manualValue.value = JSON.stringify(items.value, null, 2)
}

function onManualChange() {
  try {
    const parsed = JSON.parse(manualValue.value)
    if (Array.isArray(parsed)) {
      items.value = parsed
      emit('update:modelValue', items.value)
    }
  } catch {
    // Invalid JSON, ignore
  }
}
</script>
