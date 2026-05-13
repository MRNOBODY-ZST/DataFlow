<template>
  <div class="w-80 shrink-0 border-l border-gray-200 bg-white">
    <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3">
      <div>
        <h3 class="text-sm font-semibold text-gray-800">节点配置</h3>
        <p class="mt-0.5 text-xs text-gray-500">{{ schema?.label || node.type }}</p>
      </div>
      <button class="text-lg leading-none text-gray-400 hover:text-gray-600" @click="$emit('close')">×</button>
    </div>

    <div class="space-y-4 overflow-y-auto p-4">
      <div>
        <label class="mb-1 block text-xs font-medium text-gray-500">节点 ID</label>
        <p class="truncate font-mono text-xs text-gray-400">{{ node.id }}</p>
      </div>

      <template v-for="field in schema?.fields || []" :key="field.key">
        <div class="space-y-1.5">
          <label class="block text-xs font-medium text-gray-500">{{ field.label }}</label>

          <!-- JMESPath Builder Widget -->
          <JMESPathBuilder
            v-if="field.widget === 'jmespath'"
            v-model="localConfig[field.key]"
          />

          <!-- String Array Editor Widget -->
          <StringArrayEditor
         v-else-if="field.widget === 'string-array'"
            v-model="localConfig[field.key]"
            :placeholder="field.placeholder"
          />

        <!-- Key-Value Editor Widget -->
          <KeyValueEditor
          v-else-if="field.widget === 'key-value'"
         v-model="localConfig[field.key]"
         :key-placeholder="field.widgetConfig?.keyPlaceholder ?? undefined"
            :value-placeholder="field.widgetConfig?.valuePlaceholder ?? undefined"
       :value-type="(field.widgetConfig?.valueType as 'text' | 'select' | undefined) ?? undefined"
            :value-options="field.widgetConfig?.valueOptions ?? undefined"
      />

          <!-- Json Mapper Widget -->
          <JsonMapperWidget
            v-else-if="field.widget === 'json-mapper'"
            :model-value="localConfig[field.key]"
            :sample="localConfig['sample']"
            @update:model-value="localConfig[field.key] = $event"
            @update:sample="localConfig['sample'] = $event"
          />

          <!-- File Picker -->
       <div v-else-if="field.type === 'file-picker'" class="space-y-2">
            <div class="rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-700">
          {{ localConfig[field.key] || '未选择文件' }}
            </div>
            <div class="flex gap-2">
              <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="pickerField = field.key; showFilePicker = true">选择文件</button>
              <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50" @click="manualMode[field.key] = !manualMode[field.key]">
           {{ manualMode[field.key] ? '隐藏手动输入' : '手动输入' }}
            </button>
        </div>
        <input
              v-if="manualMode[field.key]"
              v-model="localConfig[field.key]"
              :placeholder="field.placeholder"
              class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <!-- Select -->
          <select
            v-else-if="field.type === 'select'"
      v-model="localConfig[field.key]"
       class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          >
         <option v-for="option in field.options || []" :key="option" :value="option">{{ option }}</option>
          </select>

          <!-- Number -->
       <input
            v-else-if="field.type === 'number'"
            v-model.number="localConfig[field.key]"
            type="number"
        :placeholder="field.placeholder"
        class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />

          <!-- Textarea -->
          <textarea
            v-else-if="field.type === 'textarea'"
            v-model="localConfig[field.key]"
            rows="4"
            :placeholder="field.placeholder"
            class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />

          <!-- Text (default) -->
          <input
            v-else
            v-model="localConfig[field.key]"
            :placeholder="field.placeholder"
            class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
     </div>
      </template>
    </div>
    <div class="border-t border-gray-100 p-4">
      <button class="w-full rounded-lg bg-indigo-600 py-2 text-sm font-medium text-white transition hover:bg-indigo-500" @click="apply">
        应用
      </button>
    </div>
  </div>

  <FilePickerModal :open="showFilePicker" @close="showFilePicker = false" @select="onFileSelect" />
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Node } from '@vue-flow/core'
import { useNodeSchemaStore } from '@/stores/nodeSchema'
import FilePickerModal from '@/components/ui/FilePickerModal.vue'
import JMESPathBuilder from '@/components/flow/fields/JMESPathBuilder.vue'
import StringArrayEditor from '@/components/flow/fields/StringArrayEditor.vue'
import KeyValueEditor from '@/components/flow/fields/KeyValueEditor.vue'
import JsonMapperWidget from '@/components/flow/fields/JsonMapperWidget.vue'
import type { FileMetadata } from '@/api/file'

const props = defineProps<{
  node: Node
}>()
const emit = defineEmits<{ update: [node: Node]; close: [] }>()

const nodeSchemaStore = useNodeSchemaStore()
const localConfig = ref<Record<string, any>>({ ...(props.node.data ?? {}) })
const showFilePicker = ref(false)
const pickerField = ref('key')
const manualMode = ref<Record<string, boolean>>({})

const schema = computed(() => nodeSchemaStore.byType[props.node.type])

watch(
  () => props.node.id,
  () => {
    localConfig.value = { ...(props.node.data ?? {}) }
    manualMode.value = {}
  },
)

function onFileSelect(file: FileMetadata) {
  localConfig.value[pickerField.value] = file.key
  showFilePicker.value = false
}

function apply() {
  emit('update', { ...props.node, data: { ...localConfig.value } })
}
</script>
