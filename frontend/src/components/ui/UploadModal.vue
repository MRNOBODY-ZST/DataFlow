<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-20" @close="close">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity"></div>
      </TransitionChild>

      <div class="fixed inset-0 z-20 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
              <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div class="sm:flex sm:items-start">
                  <div class="mx-auto flex size-12 shrink-0 items-center justify-center rounded-full bg-indigo-100 sm:mx-0 sm:size-10">
                    <ArrowUpTrayIcon class="size-6 text-indigo-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                    <DialogTitle as="h3" class="text-base font-semibold text-gray-900">上传文件</DialogTitle>
                    <div class="mt-4 space-y-4">
                      <label class="flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 px-6 py-8 text-center hover:border-indigo-400 hover:bg-indigo-50/40">
                        <ArrowUpTrayIcon class="size-8 text-gray-400" />
                        <span class="mt-2 text-sm font-medium text-gray-700">点击选择文件</span>
                        <span class="mt-1 text-xs text-gray-500">上传后可在节点和运行弹窗中复用</span>
                        <input class="hidden" type="file" @change="onFileChange" />
                      </label>

                      <div v-if="file" class="rounded-lg border border-gray-200 bg-white px-4 py-3">
                        <p class="text-sm font-medium text-gray-900">{{ file.name }}</p>
                        <p class="mt-1 text-xs text-gray-500">{{ prettySize(file.size) }}</p>
                      </div>

                      <div v-if="progress > 0" class="space-y-2">
                        <div class="flex items-center justify-between text-xs text-gray-500">
                          <span>上传进度</span>
                          <span>{{ progress }}%</span>
                        </div>
                        <div class="h-2 rounded-full bg-gray-200">
                          <div class="h-2 rounded-full bg-indigo-600 transition-all" :style="{ width: `${progress}%` }" />
                        </div>
                      </div>

                      <p v-if="error" class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                <button type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 sm:ml-3 sm:w-auto disabled:opacity-60" :disabled="!file || uploading" @click="upload">
                  {{ uploading ? '上传中...' : '上传' }}
                </button>
                <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto" @click="close">
                  取消
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
import { ref } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { ArrowUpTrayIcon } from '@heroicons/vue/24/outline'
import { fileApi, type FileMetadata } from '@/api/file'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: []; uploaded: [file: FileMetadata] }>()

const file = ref<File | null>(null)
const uploading = ref(false)
const progress = ref(0)
const error = ref('')

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  file.value = input.files?.[0] ?? null
  progress.value = 0
  error.value = ''
}

async function upload() {
  if (!file.value) return
  uploading.value = true
  error.value = ''
  progress.value = 0
  try {
    const { url, key } = await fileApi.presignUpload(file.value.name)
    await fileApi.uploadToMinio(url, file.value, (pct) => {
      progress.value = pct
    })
    emit('uploaded', {
      key,
      size: file.value.size,
      lastModified: new Date().toISOString(),
      bucket: 'input',
    })
    close()
  } catch (e: any) {
    error.value = e.message || '上传失败'
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
  file.value = null
  uploading.value = false
  progress.value = 0
  error.value = ''
  emit('close')
}
</script>
