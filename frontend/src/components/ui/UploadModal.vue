<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-20" @close="close">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50"></div>
      </TransitionChild>

      <div class="fixed inset-0 z-20 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
              <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div class="sm:flex sm:items-start">
                  <div class="mx-auto flex size-12 shrink-0 items-center justify-center rounded-full bg-sky-100 sm:mx-0 sm:size-10 dark:bg-sky-500/10">
                    <ArrowUpTrayIcon class="size-6 text-sky-600 dark:text-sky-400" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                    <DialogTitle as="h3" class="text-base font-semibold text-gray-900 dark:text-white">{{ t('upload.title') }}</DialogTitle>

                    <!-- Mode tabs -->
                    <div class="mt-3 flex gap-2">
                      <button
                        v-for="m in modes"
                        :key="m.key"
                        type="button"
                        class="rounded-full px-3 py-1 text-xs font-medium"
                        :class="mode === m.key
                          ? 'bg-sky-600 text-white dark:bg-sky-500'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-white/10 dark:text-gray-300 dark:hover:bg-white/20'"
                        @click="switchMode(m.key)"
                      >
                        {{ m.label }}
                      </button>
                    </div>

                    <div class="mt-4 space-y-4">
                      <!-- Dataset name (for dataset mode) -->
                      <div v-if="mode === 'dataset'" class="space-y-1.5">
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('upload.datasetName') }}</label>
                        <input
                          v-model="datasetName"
                          type="text"
                          placeholder="e.g. my-image-dataset"
                          class="w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-sky-500"
                        />
                      </div>

                      <!-- Drop zone -->
                      <label class="flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 px-6 py-8 text-center hover:border-sky-400 hover:bg-sky-50/40 dark:border-white/20 dark:bg-white/5 dark:hover:border-sky-500/50 dark:hover:bg-sky-500/5">
                        <ArrowUpTrayIcon class="size-8 text-gray-400 dark:text-gray-500" />
                        <span class="mt-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                          {{ mode === 'single' ? t('upload.clickSingle') : mode === 'batch' ? t('upload.clickBatch') : t('upload.clickFolder') }}
                        </span>
                        <span class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                          {{ mode === 'single' ? t('upload.singleDesc') : mode === 'batch' ? t('upload.batchDesc') : t('upload.datasetDesc') }}
                        </span>
                        <input
                          v-if="mode === 'single'"
                          class="hidden"
                          type="file"
                          @change="onFileChange"
                        />
                        <input
                          v-else-if="mode === 'batch'"
                          class="hidden"
                          type="file"
                          multiple
                          @change="onFilesChange"
                        />
                        <input
                          v-else
                          class="hidden"
                          type="file"
                          webkitdirectory
                          @change="onFilesChange"
                        />
                      </label>

                      <!-- File list -->
                      <div v-if="fileList.length > 0" class="max-h-48 space-y-1 overflow-y-auto rounded-lg border border-gray-200 p-2 dark:border-white/10">
                        <div v-for="(f, i) in fileList" :key="i" class="flex items-center justify-between gap-2 rounded-md px-2 py-1.5 text-sm" :class="fileStatuses[i] === 'done' ? 'bg-green-50 dark:bg-green-500/10' : fileStatuses[i] === 'error' ? 'bg-red-50 dark:bg-red-500/10' : ''">
                          <div class="min-w-0 flex-1">
                            <p class="truncate font-medium text-gray-900 dark:text-white">{{ f.name }}</p>
                            <p class="text-xs text-gray-500 dark:text-gray-400">{{ prettySize(f.size) }}</p>
                          </div>
                          <div class="flex items-center gap-2">
                            <div v-if="fileStatuses[i] === 'uploading'" class="flex items-center gap-1.5">
                              <div class="h-1.5 w-16 rounded-full bg-gray-200 dark:bg-gray-700">
                                <div class="h-1.5 rounded-full bg-sky-600 transition-all dark:bg-sky-500" :style="{ width: `${fileProgress[i] || 0}%` }" />
                              </div>
                              <span class="text-xs text-gray-500">{{ fileProgress[i] || 0 }}%</span>
                            </div>
                            <CheckCircleIcon v-else-if="fileStatuses[i] === 'done'" class="size-4 text-green-500" />
                            <ExclamationCircleIcon v-else-if="fileStatuses[i] === 'error'" class="size-4 text-red-500" />
                            <button v-else type="button" class="text-gray-400 hover:text-red-500" @click="removeFile(i)">
                              <XMarkIcon class="size-4" />
                            </button>
                          </div>
                        </div>
                      </div>

                      <!-- Summary -->
                      <div v-if="fileList.length > 1" class="text-xs text-gray-500 dark:text-gray-400">
                        {{ t('upload.filesTotal', { n: fileList.length, size: prettySize(totalSize) }) }}
                        <span v-if="completedCount > 0"> · {{ t('upload.uploaded', { done: completedCount, total: fileList.length }) }}</span>
                      </div>

                      <p v-if="error" class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-400/10 dark:text-red-400">{{ error }}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 dark:bg-gray-800/50">
                <button type="button" class="inline-flex w-full justify-center rounded-md bg-sky-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-sky-500 sm:ml-3 sm:w-auto disabled:opacity-60 dark:bg-sky-500 dark:hover:bg-sky-400" :disabled="fileList.length === 0 || uploading || (mode === 'dataset' && !datasetName.trim())" @click="upload">
                  {{ uploading ? t('upload.uploading', { done: completedCount, total: fileList.length }) : t('common.upload') }}
                </button>
                <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="close">
                  {{ t('common.cancel') }}
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { ArrowUpTrayIcon, CheckCircleIcon, ExclamationCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { fileApi, type FileMetadata } from '@/api/file'

type UploadMode = 'single' | 'batch' | 'dataset'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: []; uploaded: [file: FileMetadata] }>()

const { t } = useI18n()

const mode = ref<UploadMode>('single')
const datasetName = ref('')
const fileList = ref<File[]>([])
const fileProgress = ref<Record<number, number>>({})
const fileStatuses = ref<Record<number, 'pending' | 'uploading' | 'done' | 'error'>>({})
const uploading = ref(false)
const error = ref('')

const modes = computed(() => [
  { key: 'single' as UploadMode, label: t('upload.singleFile') },
  { key: 'batch' as UploadMode, label: t('upload.batchUpload') },
  { key: 'dataset' as UploadMode, label: t('upload.dataset') },
])

const totalSize = computed(() => fileList.value.reduce((sum, f) => sum + f.size, 0))
const completedCount = computed(() => Object.values(fileStatuses.value).filter((s) => s === 'done').length)

function switchMode(m: UploadMode) {
  mode.value = m
  fileList.value = []
  fileProgress.value = {}
  fileStatuses.value = {}
  error.value = ''
}

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    fileList.value = [file]
    fileProgress.value = {}
    fileStatuses.value = {}
  }
  error.value = ''
  input.value = ''
}

function onFilesChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    fileList.value = Array.from(input.files)
    fileProgress.value = {}
    fileStatuses.value = {}
  }
  error.value = ''
  input.value = ''
}

function removeFile(index: number) {
  fileList.value.splice(index, 1)
}

async function upload() {
  if (fileList.value.length === 0) return
  uploading.value = true
  error.value = ''

  const prefix = mode.value === 'dataset' ? datasetName.value.trim() : ''

  try {
    const results = await fileApi.uploadBatch(
      fileList.value,
      prefix,
      (i, pct) => {
        fileProgress.value[i] = pct
        fileStatuses.value[i] = 'uploading'
      },
      (i, meta) => {
        fileStatuses.value[i] = 'done'
        fileProgress.value[i] = 100
        emit('uploaded', meta)
      },
    )

    if (results.length === fileList.value.length) {
      setTimeout(() => close(), 500)
    }
  } catch (e: any) {
    error.value = e.message || 'Upload failed'
    for (let i = 0; i < fileList.value.length; i++) {
      if (fileStatuses.value[i] !== 'done') {
        fileStatuses.value[i] = 'error'
      }
    }
  } finally {
    uploading.value = false
  }
}

function prettySize(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

function close() {
  fileList.value = []
  fileProgress.value = {}
  fileStatuses.value = {}
  uploading.value = false
  error.value = ''
  datasetName.value = ''
  emit('close')
}
</script>
