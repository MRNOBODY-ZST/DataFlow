<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-50" @close="$emit('close')">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="" leave="ease-in duration-200" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/75" />
      </TransitionChild>

      <div class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 scale-95" enter-to="scale-100" leave="ease-in duration-200" leave-from="scale-100" leave-to="opacity-0 scale-95">
            <DialogPanel class="flex h-[80vh] w-full max-w-5xl transform flex-col overflow-hidden rounded-xl bg-white shadow-2xl transition-all dark:bg-gray-800">
              <!-- Header -->
              <div class="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-white/10">
                <div>
                  <DialogTitle class="text-base font-semibold text-gray-900 dark:text-white">{{ t('jsonMapper.title') }}</DialogTitle>
                  <p class="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{{ t('jsonMapper.subtitle') }}</p>
                </div>
                <button type="button" class="rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-white" @click="$emit('close')">
                  <XMarkIcon class="size-5" />
                </button>
              </div>

              <!-- Body: two panels -->
              <div class="flex flex-1 overflow-hidden">
                <!-- LEFT: Source JSON tree -->
                <div class="flex w-1/2 flex-col border-r border-gray-200 dark:border-white/10">
                  <div class="flex items-center justify-between border-b border-gray-100 px-4 py-2 dark:border-white/5">
                    <span class="text-xs font-semibold uppercase tracking-wide text-gray-400">{{ t('jsonMapper.sourceJson') }}</span>
                    <div class="flex items-center gap-2">
                      <button
                        v-if="hasUpstreamReader"
                        type="button"
                        class="flex items-center gap-1 text-xs text-emerald-600 hover:text-emerald-500 disabled:opacity-50 dark:text-emerald-400"
                        :disabled="fetchingUpstream"
                        @click="fetchFromUpstream"
                      >
                        <ArrowDownTrayIcon class="size-3.5" />
                        {{ fetchingUpstream ? t('jsonMapper.fetchingUpstream') : t('jsonMapper.fetchUpstream') }}
                      </button>
                      <button
                        type="button"
                        class="text-xs text-sky-600 hover:text-sky-500 dark:text-sky-400"
                        @click="showSampleEditor = !showSampleEditor"
                      >
                        {{ showSampleEditor ? t('jsonMapper.hideEditor') : t('jsonMapper.editSample') }}
                      </button>
                    </div>
                  </div>

                  <!-- Sample JSON editor -->
                  <div v-if="showSampleEditor" class="border-b border-gray-100 p-3 dark:border-white/5">
                    <textarea
                      v-model="sampleText"
                      rows="6"
                      placeholder='粘贴 JSON 样本，例如：&#10;{"users": [{"name": "Alice", "age": 30}]}'
                      class="w-full rounded-md border-0 bg-gray-50 px-3 py-2 font-mono text-xs text-gray-700 ring-1 ring-gray-200 focus:ring-2 focus:ring-sky-500 dark:bg-gray-700 dark:text-gray-200 dark:ring-gray-600"
                      @input="parseSample"
                    />
                    <p v-if="parseError" class="mt-1 text-xs text-red-500">{{ parseError }}</p>
                  </div>

                  <!-- Fetch error -->
                  <div v-if="fetchError" class="border-b border-gray-100 px-4 py-1.5 dark:border-white/5">
                    <p class="text-xs text-red-500">{{ fetchError }}</p>
                  </div>

                  <!-- Tree view -->
                  <div class="flex-1 overflow-y-auto p-3">
                    <div v-if="!parsedSample" class="flex h-full items-center justify-center">
                      <div class="text-center">
                        <p class="text-sm text-gray-400 dark:text-gray-500">
                          {{ t('jsonMapper.emptySourceHint') }}
                        </p>
                        <button
                          v-if="hasUpstreamReader"
                          type="button"
                          class="mt-3 inline-flex items-center gap-1.5 rounded-md bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400 dark:hover:bg-emerald-500/20"
                          :disabled="fetchingUpstream"
                          @click="fetchFromUpstream"
                        >
                          <ArrowDownTrayIcon class="size-3.5" />
                          {{ fetchingUpstream ? t('jsonMapper.fetchingUpstream') : t('jsonMapper.fetchUpstream') }}
                        </button>
                      </div>
                    </div>
                    <JsonFieldTree v-else :json="parsedSample" @drag-field="onSourceDrag" />
                  </div>
                </div>

                <!-- RIGHT: Target mappings -->
                <div class="flex w-1/2 flex-col">
                  <div class="flex items-center justify-between border-b border-gray-100 px-4 py-2 dark:border-white/5">
                    <span class="text-xs font-semibold uppercase tracking-wide text-gray-400">{{ t('jsonMapper.outputMapping') }}</span>
                    <span class="text-[10px] text-gray-400">{{ t('jsonMapper.nFields', { n: mappings.length }) }}</span>
                  </div>

                  <!-- Drop zone / mapping list -->
                  <div
                    class="flex-1 overflow-y-auto p-3"
                    @dragover.prevent="onDragOver"
                    @dragenter.prevent="dragCounter++; dropHighlight = true"
                    @dragleave="dragCounter--; if (dragCounter <= 0) { dragCounter = 0; dropHighlight = false }"
                    @drop.prevent="onDrop"
                  >
                    <div
                      v-if="mappings.length === 0"
                      class="flex h-full items-center justify-center rounded-lg border-2 border-dashed transition-colors"
                      :class="dropHighlight ? 'border-sky-400 bg-sky-50 dark:border-sky-500 dark:bg-sky-500/10' : 'border-gray-200 dark:border-gray-600'"
                    >
                      <p class="text-center text-sm text-gray-400 dark:text-gray-500">
                        {{ t('jsonMapper.emptyDropHint') }}
                      </p>
                    </div>

                    <div v-else class="space-y-2">
                      <div
                        v-for="(m, idx) in mappings"
                        :key="idx"
                        class="group flex items-start gap-2 rounded-lg border border-gray-200 bg-gray-50 p-3 transition-colors hover:border-sky-200 hover:bg-sky-50/50 dark:border-gray-600 dark:bg-gray-700 dark:hover:border-sky-500/30"
                      >
                        <!-- Source path (read-only chip) -->
                        <div class="w-[45%] shrink-0 space-y-1">
                          <label class="block text-[10px] font-medium text-gray-400">{{ t('jsonMapper.sourcePath') }}</label>
                          <div class="flex items-center gap-1 rounded bg-blue-50 px-2 py-1 text-xs font-mono text-blue-700 dark:bg-blue-500/10 dark:text-blue-300">
                            <ArrowLongRightIcon class="size-3 shrink-0 text-blue-400" />
                            <span class="truncate">{{ m.source }}</span>
                          </div>
                        </div>

                        <!-- Target path (editable) -->
                        <div class="flex-1 space-y-1">
                          <label class="block text-[10px] font-medium text-gray-400">{{ t('jsonMapper.targetName') }}</label>
                          <input
                            v-model="m.target"
                            class="w-full rounded border-0 bg-white px-2 py-1 text-xs ring-1 ring-gray-200 focus:ring-2 focus:ring-sky-500 dark:bg-gray-600 dark:text-gray-200 dark:ring-gray-500"
                            :placeholder="t('jsonMapper.targetPlaceholder')"
                          />
                        </div>

                        <!-- Default value -->
                        <div class="w-20 shrink-0 space-y-1">
                          <label class="block text-[10px] font-medium text-gray-400">{{ t('jsonMapper.defaultValue') }}</label>
                          <input
                            v-model="m.default"
                            class="w-full rounded border-0 bg-white px-2 py-1 text-xs ring-1 ring-gray-200 focus:ring-2 focus:ring-sky-500 dark:bg-gray-600 dark:text-gray-200 dark:ring-gray-500"
                            placeholder="—"
                          />
                        </div>

                        <!-- Remove button -->
                        <button
                          type="button"
                          class="mt-4 shrink-0 rounded p-1 text-gray-300 opacity-0 transition-opacity hover:bg-red-50 hover:text-red-500 group-hover:opacity-100 dark:hover:bg-red-500/10"
                          @click="removeMapping(idx)"
                        >
                          <TrashIcon class="size-3.5" />
                        </button>
                      </div>

                      <!-- Trailing drop zone -->
                      <div
                        class="flex h-12 items-center justify-center rounded-lg border-2 border-dashed transition-colors"
                        :class="dropHighlight ? 'border-sky-400 bg-sky-50 dark:border-sky-500 dark:bg-sky-500/10' : 'border-gray-200 dark:border-gray-600'"
                      >
                        <span class="text-xs text-gray-400">{{ t('jsonMapper.dropMore') }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Add manually -->
                  <div class="border-t border-gray-100 px-4 py-2 dark:border-white/5">
                    <button
                      type="button"
                      class="w-full rounded-md border border-dashed border-gray-300 px-3 py-1.5 text-xs text-gray-500 transition-colors hover:border-sky-300 hover:text-sky-600 dark:border-gray-600 dark:hover:border-sky-500 dark:hover:text-sky-400"
                      @click="addManualMapping"
                    >
                      {{ t('jsonMapper.addMapping') }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Footer -->
              <div class="flex items-center justify-between border-t border-gray-200 px-6 py-3 dark:border-white/10">
                <div class="text-xs text-gray-400">
                  {{ t('jsonMapper.tip') }} <code class="rounded bg-gray-100 px-1 dark:bg-gray-700">user.name</code>
                </div>
                <div class="flex gap-2">
                  <button
                    type="button"
                    class="rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20"
                    @click="$emit('close')"
                  >{{ t('common.cancel') }}</button>
                  <button
                    type="button"
                    class="rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white shadow-xs hover:bg-sky-500 dark:bg-sky-500 dark:hover:bg-sky-400"
                    @click="apply"
                  >{{ t('jsonMapper.applyMapping') }}</button>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon, TrashIcon, ArrowLongRightIcon, ArrowDownTrayIcon } from '@heroicons/vue/24/outline'
import type { Node } from '@vue-flow/core'
import JsonFieldTree from './JsonFieldTree.vue'
import { fileApi } from '@/api/file'

interface MappingEntry {
  source: string
  target: string
  default?: string
}

const props = defineProps<{
  open: boolean
  modelValue: MappingEntry[]
  sample?: string
  upstreamNodes?: Node[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: MappingEntry[]]
  'update:sample': [value: string]
  close: []
}>()

const { t } = useI18n()

const mappings = ref<MappingEntry[]>([])
const sampleText = ref('')
const parsedSample = ref<any>(null)
const parseError = ref('')
const showSampleEditor = ref(false)
const dropHighlight = ref(false)
const dragCounter = ref(0)
const fetchingUpstream = ref(false)
const fetchError = ref('')

const hasUpstreamReader = computed(() => {
  if (!props.upstreamNodes?.length) return false
  return props.upstreamNodes.some(n =>
    ['json_reader', 'minio_reader'].includes(n.type)
  )
})

watch(() => props.open, (val) => {
  if (val) {
    mappings.value = (props.modelValue ?? []).map(m => ({ ...m }))
    sampleText.value = props.sample ?? ''
    dragCounter.value = 0
    dropHighlight.value = false
    parseSample()
    if (!parsedSample.value) showSampleEditor.value = true
  }
})

function parseSample() {
  parseError.value = ''
  const text = sampleText.value.trim()
  if (!text) {
    parsedSample.value = null
    return
  }
  try {
    parsedSample.value = JSON.parse(text)
  } catch (e: any) {
    parseError.value = `${t('jsonMapper.parseError', { msg: e.message })}`
    parsedSample.value = null
  }
}

async function fetchFromUpstream() {
  if (!props.upstreamNodes?.length) return
  const reader = props.upstreamNodes.find(n =>
    ['json_reader', 'minio_reader'].includes(n.type)
  )
  if (!reader) {
    fetchError.value = t('jsonMapper.noUpstreamReader')
    return
  }
  const key = reader.data?.key as string | undefined
  if (!key) {
    fetchError.value = t('jsonMapper.noUpstreamReader')
    return
  }

  fetchingUpstream.value = true
  fetchError.value = ''
  try {
    const { url } = await fileApi.presignDownload(key, 'input')
    const resp = await fetch(url)
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const text = await resp.text()
    sampleText.value = text
    showSampleEditor.value = false
    parseSample()
  } catch (e: any) {
    fetchError.value = t('jsonMapper.fetchUpstreamError', { msg: e.message || String(e) })
  } finally {
    fetchingUpstream.value = false
  }
}

function onSourceDrag(_path: string, _type: string) {
  // visual feedback handled by tree component
}

function onDragOver(event: DragEvent) {
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'copy'
  }
}

function onDrop(event: DragEvent) {
  dropHighlight.value = false
  dragCounter.value = 0
  const raw = event.dataTransfer?.getData('application/json-field')
  if (!raw) return
  try {
    const { path } = JSON.parse(raw) as { path: string; type: string }
    const target = path.replace(/\.\[\*\]/g, '')
    if (!mappings.value.some(m => m.source === path)) {
      mappings.value.push({ source: path, target })
    }
  } catch {
    // ignore
  }
}

function addManualMapping() {
  mappings.value.push({ source: '', target: '' })
}

function removeMapping(idx: number) {
  mappings.value.splice(idx, 1)
}

function apply() {
  const cleaned = mappings.value
    .filter(m => m.source || m.target)
    .map(m => {
      const entry: MappingEntry = { source: m.source, target: m.target || m.source }
      if (m.default) entry.default = m.default
      return entry
    })
  emit('update:modelValue', cleaned)
  emit('update:sample', sampleText.value)
  emit('close')
}
</script>
