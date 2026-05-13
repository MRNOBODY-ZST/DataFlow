<template>
  <div class="space-y-3">
    <div class="space-y-2">
      <div class="text-xs font-medium text-gray-600">路径构建器</div>

      <div class="space-y-2">
        <div v-for="(segment, index) in pathSegments" :key="index" class="flex items-center gap-2">
          <span v-if="index > 0" class="text-gray-400">.</span>
          <input
            v-model="pathSegments[index]"
            type="text"
            placeholder="字段名或 [*]"
            class="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
            @input="updateExpression"
          />
          <button
       v-if="pathSegments.length > 1"
            type="button"
            class="rounded-md bg-red-50 px-2 py-2 text-sm text-red-600 hover:bg-red-100"
            @click="removeSegment(index)"
          >
            ×
       </button>
        </div>
      </div>

      <div class="flex gap-2">
    <button
          type="button"
          class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
          @click="addSegment"
        >
      + 添加字段
        </button>
        <button
          type="button"
          class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
          @click="addProjection"
    >
          + 数组投影 [*]
        </button>
      </div>
    </div>

    <div class="space-y-1">
      <div class="flex items-center justify-between">
        <div class="text-xs font-medium text-gray-600">生成的表达式</div>
        <button
          type="button"
          class="text-xs text-indigo-600 hover:text-indigo-700"
          @click="showManual = !showManual"
        >
          {{ showManual ? '使用构建器' : '手动编辑' }}
        </button>
      </div>

      <div v-if="!showManual" class="rounded-md border border-gray-300 bg-gray-50 px-3 py-2 font-mono text-sm text-gray-700">
        {{ expression || '(空)' }}
      </div>

      <textarea
        v-else
      v-model="manualExpression"
        rows="3"
        placeholder="items[*].name"
        class="w-full rounded-md border border-gray-300 px-3 py-2 font-mono text-sm focus:border-indigo-500 focus:outline-none"
        @input="onManualChange"
      />
    </div>

    <div class="rounded-md bg-blue-50 px-3 py-2 text-xs text-blue-700">
      <div class="font-medium">提示</div>
      <ul class="mt-1 list-inside list-disc space-y-0.5">
        <li>使用 [*] 表示数组投影</li>
        <li>字段名用 . 连接</li>
        <li>支持手动编辑完整 JMESPath 表达式</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: string | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
const pathSegments = ref<string[]>([''])
const expression = ref('')
const showManual = ref(false)
const manualExpression = ref('')

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue && typeof newValue === 'string') {
      expression.value = newValue
      manualExpression.value = newValue

      // Try to parse simple paths back into segments
      if (!showManual.value) {
        const segments = newValue.split(/\.(?![^\[]*\])/)
      if (segments.length > 0 && !newValue.includes('(') && !newValue.includes('|')) {
          pathSegments.value = segments
        }
      }
    } else {
      expression.value = ''
      manualExpression.value = ''
      pathSegments.value = ['']
    }
  },
  { immediate: true },
)

function addSegment() {
  pathSegments.value.push('')
  updateExpression()
}

function addProjection() {
  pathSegments.value.push('[*]')
  updateExpression()
}

function removeSegment(index: number) {
  pathSegments.value.splice(index, 1)
  if (pathSegments.value.length === 0) {
    pathSegments.value = ['']
  }
  updateExpression()
}

function updateExpression() {
  const filtered = pathSegments.value.filter((s) => s.trim())
  expression.value = filtered.join('.')
  manualExpression.value = expression.value
  emit('update:modelValue', expression.value)
}

function onManualChange() {
  expression.value = manualExpression.value
  emit('update:modelValue', manualExpression.value)
}
</script>
