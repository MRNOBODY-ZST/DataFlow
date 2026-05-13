<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-20" @close="close">
      <TransitionChild as="template" enter="ease-in-out duration-500" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in-out duration-500" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity"></div>
      </TransitionChild>

      <div class="fixed inset-0 overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10 sm:pl-16">
            <TransitionChild as="template" enter="transform transition ease-in-out duration-500 sm:duration-700" enter-from="translate-x-full" enter-to="translate-x-0" leave="transform transition ease-in-out duration-500 sm:duration-700" leave-from="translate-x-0" leave-to="translate-x-full">
              <DialogPanel class="pointer-events-auto relative w-screen max-w-md">
                <TransitionChild as="template" enter="ease-in-out duration-500" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in-out duration-500" leave-from="opacity-100" leave-to="opacity-0">
                  <div class="absolute top-0 left-0 -ml-8 flex pt-4 pr-2 sm:-ml-10 sm:pr-4">
                    <button type="button" class="relative rounded-md text-gray-300 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600" @click="close">
                      <span class="absolute -inset-2.5"></span>
                      <span class="sr-only">Close panel</span>
                      <XMarkIcon class="size-6" aria-hidden="true" />
                    </button>
                  </div>
                </TransitionChild>
                <div class="relative flex h-full flex-col overflow-y-auto bg-white p-8">
                  <div class="space-y-6 pb-16" v-if="file">
                    <div>
                      <div class="flex size-16 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700">
                        <DocumentIcon class="size-8" />
                      </div>
                      <div class="mt-4 flex items-start justify-between">
                        <div>
                          <h2 class="text-base font-semibold text-gray-900">{{ file.key.split('/').pop() }}</h2>
                          <p class="text-sm font-medium text-gray-500">{{ prettySize(file.size) }}</p>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h3 class="font-medium text-gray-900">Information</h3>
                      <dl class="mt-2 divide-y divide-gray-200 border-y border-gray-200">
                        <div class="flex justify-between py-3 text-sm">
                          <dt class="text-gray-500">Bucket</dt>
                          <dd class="text-gray-900">{{ file.bucket }}</dd>
                        </div>
                        <div class="flex justify-between gap-4 py-3 text-sm">
                          <dt class="text-gray-500">Object Key</dt>
                          <dd class="break-all text-right text-gray-900">{{ file.key }}</dd>
                        </div>
                        <div class="flex justify-between py-3 text-sm">
                          <dt class="text-gray-500">Last Modified</dt>
                          <dd class="text-gray-900">{{ formatDate(file.lastModified) }}</dd>
                        </div>
                      </dl>
                    </div>
                    <div class="flex gap-3">
                      <button type="button" class="flex-1 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="download">下载</button>
                      <button
                        v-if="file.bucket === 'input'"
                        type="button"
                        class="flex-1 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50"
                        @click="remove"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { Dialog, DialogPanel, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { DocumentIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { fileApi, type FileMetadata } from '@/api/file'

const props = defineProps<{
  open: boolean
  file: FileMetadata | null
}>()

const emit = defineEmits<{ close: []; deleted: [file: FileMetadata] }>()

async function download() {
  if (!props.file) return
  const { url } = await fileApi.presignDownload(props.file.key, props.file.bucket)
  window.open(url, '_blank')
}

async function remove() {
  if (!props.file || props.file.bucket !== 'input') return
  await fileApi.deleteFile(props.file.bucket, props.file.key)
  emit('deleted', props.file)
  close()
}

function prettySize(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

function close() {
  emit('close')
}
</script>
