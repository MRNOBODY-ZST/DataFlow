<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-20" @close="close">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity"></div>
      </TransitionChild>

      <div class="fixed inset-0 z-20 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-3xl">
              <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div class="flex items-center justify-between">
                  <DialogTitle as="h3" class="text-base font-semibold text-gray-900">选择文件</DialogTitle>
                  <button type="button" class="rounded-md p-1 text-gray-400 hover:text-gray-600" @click="close">
                    <XMarkIcon class="size-5" />
                  </button>
                </div>

                <div class="mt-4 space-y-4">
                  <div class="flex items-center gap-2">
                    <input
                      v-model="search"
                      type="text"
                      placeholder="按 key 搜索"
                      class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                    />
                    <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50" @click="refresh">刷新</button>
                  </div>

                  <div class="max-h-96 overflow-y-auto rounded-lg border border-gray-200">
                    <div v-if="loading" class="px-4 py-10 text-center text-sm text-gray-500">加载中...</div>
                    <div v-else-if="filteredFiles.length === 0" class="px-4 py-10 text-center text-sm text-gray-500">暂无可选文件</div>
                    <ul v-else role="list" class="divide-y divide-gray-200">
                      <li
                        v-for="file in filteredFiles"
                        :key="file.key"
                        class="flex items-center justify-between gap-4 px-4 py-3 hover:bg-gray-50"
                      >
                        <div class="min-w-0">
                          <p class="truncate text-sm font-medium text-gray-900">{{ file.key }}</p>
                          <p class="mt-1 text-xs text-gray-500">{{ prettySize(file.size) }} · {{ formatDate(file.lastModified) }}</p>
                        </div>
                        <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="select(file)">选择</button>
                      </li>
                    </ul>
                  </div>
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
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useFileStore } from '@/stores/file'
import type { FileMetadata } from '@/api/file'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: []; select: [file: FileMetadata] }>()

const fileStore = useFileStore()
const search = ref('')

const loading = computed(() => fileStore.loading)
const filteredFiles = computed(() =>
  fileStore.files.filter((file) => file.key.toLowerCase().includes(search.value.trim().toLowerCase())),
)

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      fileStore.setBucket('input')
      await fileStore.fetchFiles('input')
    }
  },
)

async function refresh() {
  await fileStore.fetchFiles('input')
}

function select(file: FileMetadata) {
  emit('select', file)
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
  search.value = ''
  emit('close')
}
</script>
