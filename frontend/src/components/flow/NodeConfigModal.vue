<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-50" @close="$emit('close')">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="" leave="ease-in duration-200" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50"></div>
      </TransitionChild>

      <div class="fixed inset-0 z-50 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to=" translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from=" translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6 dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
              <div>
                <div class="mx-auto flex size-12 items-center justify-center rounded-full bg-sky-100 dark:bg-sky-500/10">
                  <Cog6ToothIcon class="size-6 text-sky-600 dark:text-sky-400" aria-hidden="true" />
                </div>
                <div class="mt-3 text-center sm:mt-5">
                  <DialogTitle as="h3" class="text-base font-semibold text-gray-900 dark:text-white">
                    {{ schema?.label || node?.type || t('editor.nodeConfig') }}
                  </DialogTitle>
                  <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ node?.id }}</p>
                </div>
              </div>

              <div class="mt-5 space-y-4 max-h-96 overflow-y-auto">
                <template v-for="field in schema?.fields || []" :key="field.key">
                  <div v-if="isFieldVisible(field)" class="space-y-1.5">
                    <label v-if="field.type !== 'checkbox'" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ field.label }}</label>

                    <div v-if="field.type === 'checkbox'" class="flex items-center gap-3">
                      <button
                        type="button"
                        role="switch"
                        :aria-checked="!!localConfig[field.key]"
                        class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-sky-600 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
                        :class="localConfig[field.key] ? 'bg-sky-600 dark:bg-sky-500' : 'bg-gray-200 dark:bg-gray-600'"
                        @click="localConfig[field.key] = !localConfig[field.key]"
                      >
                        <span
                          class="pointer-events-none inline-block size-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                          :class="localConfig[field.key] ? 'translate-x-5' : 'translate-x-0'"
                        />
                      </button>
                      <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ field.label }}</span>
                    </div>

                    <JMESPathBuilder v-else-if="field.widget === 'jmespath'" v-model="localConfig[field.key]" />

                    <StringArrayEditor v-else-if="field.widget === 'string-array'" v-model="localConfig[field.key]" :placeholder="field.placeholder" />

                    <KeyValueEditor
                      v-else-if="field.widget === 'key-value'"
                      v-model="localConfig[field.key]"
                      :key-placeholder="field.widgetConfig?.keyPlaceholder ?? undefined"
                      :value-placeholder="field.widgetConfig?.valuePlaceholder ?? undefined"
                      :value-type="(field.widgetConfig?.valueType as 'text' | 'select' | undefined) ?? undefined"
                      :value-options="field.widgetConfig?.valueOptions ?? undefined"
                    />

                    <JsonMapperWidget
                      v-else-if="field.widget === 'json-mapper'"
                      :model-value="localConfig[field.key]"
                      :sample="localConfig['sample']"
                      :upstream-nodes="upstreamNodes"
                      @update:model-value="localConfig[field.key] = $event"
                      @update:sample="localConfig['sample'] = $event"
                    />

                    <div v-else-if="field.type === 'file-picker'" class="space-y-2">
                      <div class="rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-700 dark:border-white/10 dark:bg-white/5 dark:text-gray-300">
                        {{ localConfig[field.key] || t('editor.noFileSelected') }}
                      </div>
                      <div class="flex gap-2">
                        <button type="button" class="rounded-md bg-sky-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-sky-500 dark:bg-sky-500 dark:hover:bg-sky-400" @click="pickerField = field.key; showFilePicker = true">{{ t('editor.choose') }}</button>
                        <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="manualMode[field.key] = !manualMode[field.key]">
                          {{ manualMode[field.key] ? t('editor.hideManual') : t('editor.manualInput') }}
                        </button>
                      </div>
                      <input
                        v-if="manualMode[field.key]"
                        v-model="localConfig[field.key]"
                        :placeholder="field.placeholder"
                        class="w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:focus:outline-sky-500"
                      />
                    </div>

                    <select
                      v-else-if="field.type === 'select'"
                      v-model="localConfig[field.key]"
                      class="w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:focus:outline-sky-500"
                    >
                      <option v-for="option in field.options || []" :key="option" :value="option">{{ option }}</option>
                    </select>

                    <input
                      v-else-if="field.type === 'number'"
                      v-model.number="localConfig[field.key]"
                      type="number"
                      :placeholder="field.placeholder"
                      class="w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:focus:outline-sky-500"
                    />

                    <textarea
                      v-else-if="field.type === 'textarea'"
                      v-model="localConfig[field.key]"
                      rows="3"
                      :placeholder="field.placeholder"
                      class="w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:focus:outline-sky-500"
                    />

                    <input
                      v-else
                      v-model="localConfig[field.key]"
                      :placeholder="field.placeholder"
                      class="w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:focus:outline-sky-500"
                    />
                  </div>
                </template>
              </div>

              <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                <button type="button" class="inline-flex w-full justify-center rounded-md bg-sky-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-sky-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600 sm:col-start-2 dark:bg-sky-500 dark:shadow-none dark:hover:bg-sky-400 dark:focus-visible:outline-sky-500" @click="apply">{{ t('common.apply') }}</button>
                <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20" @click="$emit('close')">{{ t('common.cancel') }}</button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>

      <FilePickerModal :open="showFilePicker" :initial-mode="pickerField === 'prefix' ? 'folder' : 'file'" @close="showFilePicker = false" @select="onFileSelect" @select-folder="onFolderSelect" />
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { Cog6ToothIcon } from '@heroicons/vue/24/outline'
import type { Node, Edge } from '@vue-flow/core'
import { useNodeSchemaStore } from '@/stores/nodeSchema'
import FilePickerModal from '@/components/ui/FilePickerModal.vue'
import JMESPathBuilder from '@/components/flow/fields/JMESPathBuilder.vue'
import StringArrayEditor from '@/components/flow/fields/StringArrayEditor.vue'
import KeyValueEditor from '@/components/flow/fields/KeyValueEditor.vue'
import JsonMapperWidget from '@/components/flow/fields/JsonMapperWidget.vue'
import type { FileMetadata } from '@/api/file'

const props = defineProps<{ open: boolean; node: Node | null; edges?: Edge[]; allNodes?: Node[] }>()
const emit = defineEmits<{ update: [node: Node]; close: [] }>()

const { t } = useI18n()
const nodeSchemaStore = useNodeSchemaStore()
const localConfig = ref<Record<string, any>>({})
const showFilePicker = ref(false)
const pickerField = ref('key')
const manualMode = ref<Record<string, boolean>>({})

const schema = computed(() => props.node ? nodeSchemaStore.byType[props.node.type] : null)

const upstreamNodes = computed(() => {
  if (!props.node || !props.edges || !props.allNodes) return []
  const srcIds = props.edges
    .filter(e => e.target === props.node!.id)
    .map(e => e.source)
  return props.allNodes.filter(n => srcIds.includes(n.id))
})

watch(
  () => props.node?.id,
  () => {
    localConfig.value = { ...(props.node?.data ?? {}) }
    manualMode.value = {}
  },
)

watch(
  () => props.open,
  (val) => {
    if (val && props.node) {
      localConfig.value = { ...(props.node.data ?? {}) }
      manualMode.value = {}
    }
  },
)

function onFileSelect(file: FileMetadata) {
  localConfig.value[pickerField.value] = file.key
  showFilePicker.value = false
}

function onFolderSelect(prefix: string) {
  localConfig.value[pickerField.value] = prefix
  showFilePicker.value = false
}

function isFieldVisible(_field: { key: string }) {
  return true
}

function apply() {
  if (!props.node) return
  emit('update', { ...props.node, data: { ...localConfig.value } })
  emit('close')
}
</script>
