<template>
  <div class="w-72 bg-white border-l border-gray-200 flex flex-col shrink-0">
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
      <h3 class="font-semibold text-sm text-gray-800">节点配置</h3>
      <button class="text-gray-400 hover:text-gray-600 text-lg leading-none" @click="$emit('close')">×</button>
    </div>

    <div class="flex-1 overflow-y-auto p-4 space-y-4">
      <div>
        <label class="block text-xs font-medium text-gray-500 mb-1">节点类型</label>
        <p class="text-sm text-gray-800 font-mono">{{ node.type }}</p>
      </div>

      <div>
        <label class="block text-xs font-medium text-gray-500 mb-1">节点 ID</label>
        <p class="text-xs text-gray-400 font-mono truncate">{{ node.id }}</p>
      </div>

      <!-- Dynamic config fields based on node type -->
      <template v-for="field in configFields" :key="field.key">
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">{{ field.label }}</label>
          <input
            v-if="field.type === 'text'"
            v-model="localConfig[field.key]"
            :placeholder="field.placeholder"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <input
            v-else-if="field.type === 'number'"
            v-model.number="localConfig[field.key]"
            type="number"
            :placeholder="field.placeholder"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <textarea
            v-else-if="field.type === 'textarea'"
            v-model="localConfig[field.key]"
            :placeholder="field.placeholder"
            rows="3"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 resize-none"
          />
        </div>
      </template>
    </div>

    <div class="p-4 border-t border-gray-100">
      <button
        class="w-full bg-indigo-600 text-white text-sm font-medium py-2 rounded-lg hover:bg-indigo-500 transition"
        @click="apply"
      >
        应用
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Node } from '@vue-flow/core'

const props = defineProps<{ node: Node }>()
const emit = defineEmits<{ update: [node: Node]; close: [] }>()

const localConfig = ref<Record<string, any>>({ ...(props.node.data ?? {}) })

watch(() => props.node.id, () => {
  localConfig.value = { ...(props.node.data ?? {}) }
})

const configFields = computed(() => {
  switch (props.node.type) {
    case 'csv_reader':
    case 'json_reader':
    case 'minio_reader':
      return [{ key: 'key', label: 'MinIO 对象 Key', type: 'text', placeholder: 'input/xxx/file.csv' }]
    case 'filter':
      return [{ key: 'query', label: 'Pandas Query 表达式', type: 'text', placeholder: 'age > 18' }]
    case 'map':
      return [
        { key: 'rename', label: 'Rename (JSON: {"old":"new"})', type: 'textarea', placeholder: '{"col_a": "colA"}' },
        { key: 'select', label: '保留列 (JSON 数组)', type: 'text', placeholder: '["colA","colB"]' },
      ]
    case 'aggregate':
      return [
        { key: 'group_by', label: '分组列 (JSON 数组)', type: 'text', placeholder: '["category"]' },
        { key: 'agg', label: '聚合方法 (JSON)', type: 'textarea', placeholder: '{"amount":"sum"}' },
      ]
    case 'image_resize':
      return [
        { key: 'width', label: '宽度 (px)', type: 'number', placeholder: '800' },
        { key: 'height', label: '高度 (px)', type: 'number', placeholder: '600' },
        { key: 'format', label: '输出格式', type: 'text', placeholder: 'JPEG' },
      ]
    case 'image_ocr':
      return [{ key: 'lang', label: '语言 (JSON 数组)', type: 'text', placeholder: '["ch_sim","en"]' }]
    case 'video_extract':
      return [
        { key: 'fps', label: '抽帧率 (FPS)', type: 'number', placeholder: '1' },
        { key: 'output_prefix', label: '输出前缀', type: 'text', placeholder: 'frames/task1/' },
      ]
    case 'minio_writer':
      return [
        { key: 'key', label: '输出 Key', type: 'text', placeholder: 'output/result.csv' },
        { key: 'bucket', label: 'Bucket', type: 'text', placeholder: 'dataflow-output' },
      ]
    default:
      return []
  }
})

function apply() {
  emit('update', { ...props.node, data: { ...localConfig.value } })
}
</script>
