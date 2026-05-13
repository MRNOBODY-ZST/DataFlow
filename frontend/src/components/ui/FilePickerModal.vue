<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-60" @close="close">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50"></div>
      </TransitionChild>

      <div class="fixed inset-0 z-60 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-3xl dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
              <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div class="flex items-center justify-between">
                  <DialogTitle as="h3" class="text-base font-semibold text-gray-900 dark:text-white">{{ t('filePicker.selectFile') }}</DialogTitle>
                  <button type="button" class="rounded-md p-1 text-gray-400 hover:text-gray-600 dark:hover:text-white" @click="close">
                    <XMarkIcon class="size-5" />
                  </button>
                </div>

                <div class="mt-4 space-y-4">
                  <!-- Mode toggle -->
                  <div class="flex items-center gap-2">
                    <button
                      v-for="m in pickerModes"
                      :key="m.key"
                      type="button"
                      class="rounded-full px-3 py-1 text-xs font-medium"
                      :class="pickerMode === m.key
                        ? 'bg-indigo-600 text-white dark:bg-indigo-500'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-white/10 dark:text-gray-300 dark:hover:bg-white/20'"
                      @click="pickerMode = m.key"
                    >
                      {{ m.label }}
                    </button>
                  </div>

                  <div class="flex items-center gap-2">
                    <input
                      v-model="search"
                      type="text"
                      :placeholder="t('filePicker.searchByKey')"
                      class="w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500"
                    />
                    <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="refresh">{{ t('common.refresh') }}</button>
                  </div>

                  <!-- Folder breadcrumb -->
                  <div v-if="pickerMode === 'folder' && currentPrefix" class="flex items-center gap-1 text-sm">
                    <button type="button" class="text-indigo-600 hover:text-indigo-500 dark:text-indigo-400" @click="navigateToPrefix('')">{{ t('filePicker.root') }}</button>
                    <template v-for="(seg, i) in prefixSegments" :key="i">
                      <ChevronRightIcon class="size-3 text-gray-400" />
                      <button type="button" class="text-indigo-600 hover:text-indigo-500 dark:text-indigo-400" @click="navigateToPrefix(prefixSegments.slice(0, i + 1).join('/') + '/')">{{ seg }}</button>
                    </template>
                  </div>

                  <div class="max-h-96 overflow-y-auto rounded-lg border border-gray-200 dark:border-white/10">
                    <div v-if="loading" class="px-4 py-10 text-center text-sm text-gray-500 dark:text-gray-400">{{ t('common.loading') }}</div>
                    <div v-else-if="displayItems.length === 0" class="px-4 py-10 text-center text-sm text-gray-500 dark:text-gray-400">{{ t('filePicker.noFiles') }}</div>
                    <ul v-else role="list" class="divide-y divide-gray-200 dark:divide-white/10">
                      <!-- Folders (in folder mode) -->
                      <li
                        v-for="folder in folders"
                        :key="'folder:' + folder"
                        class="flex cursor-pointer items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-white/5"
                        @click="navigateToPrefix(folder)"
                      >
                        <FolderIcon class="size-5 text-amber-500" />
                        <div class="min-w-0 flex-1">
                          <p class="truncate text-sm font-medium text-gray-900 dark:text-white">{{ folderName(folder) }}</p>
                        </div>
                        <button
                          type="button"
                          class="rounded-md bg-amber-500 px-3 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-amber-400"
                          @click.stop="selectFolder(folder)"
                        >
                          {{ t('filePicker.selectFolder') }}
                        </button>
                      </li>
                      <!-- Files -->
                      <li
                        v-for="file in filteredFiles"
                        :key="file.key"
                        class="flex items-center justify-between gap-4 px-4 py-3 hover:bg-gray-50 dark:hover:bg-white/5"
                      >
                        <div class="min-w-0">
                          <p class="truncate text-sm font-medium text-gray-900 dark:text-white">{{ pickerMode === 'folder' ? fileName(file.key) : file.key }}</p>
                          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ prettySize(file.size) }} · {{ formatDate(file.lastModified) }}</p>
                        </div>
                        <button type="button" class="shrink-0 rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="select(file)">{{ t('common.select') }}</button>
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
import { useI18n } from 'vue-i18n'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon, FolderIcon } from '@heroicons/vue/24/outline'
import { ChevronRightIcon } from '@heroicons/vue/20/solid'
import { useFileStore } from '@/stores/file'
import { fileApi, type FileMetadata } from '@/api/file'

type PickerMode = 'file' | 'folder'

const props = defineProps<{ open: boolean; initialMode?: 'file' | 'folder' }>()
const emit = defineEmits<{ close: []; select: [file: FileMetadata]; 'select-folder': [prefix: string] }>()

const { t } = useI18n()

const fileStore = useFileStore()
const search = ref('')
const pickerMode = ref<PickerMode>('file')
const currentPrefix = ref('')
const allFiles = ref<FileMetadata[]>([])

const loading = computed(() => fileStore.loading)

const pickerModes = computed(() => [
  { key: 'file' as PickerMode, label: t('filePicker.singleFile') },
  { key: 'folder' as PickerMode, label: t('filePicker.folderDataset') },
])

const prefixSegments = computed(() =>
  currentPrefix.value.replace(/\/$/, '').split('/').filter(Boolean),
)

const folders = computed(() => {
  if (pickerMode.value !== 'folder') return []
  const prefixLen = currentPrefix.value.length
  const seen = new Set<string>()
  for (const f of allFiles.value) {
    if (!f.key.startsWith(currentPrefix.value)) continue
    const rest = f.key.slice(prefixLen)
    const slashIdx = rest.indexOf('/')
    if (slashIdx > 0) {
      seen.add(currentPrefix.value + rest.slice(0, slashIdx + 1))
    }
  }
  return Array.from(seen).sort()
})

const filteredFiles = computed(() => {
  const q = search.value.trim().toLowerCase()
  let files = pickerMode.value === 'folder'
    ? allFiles.value.filter((f) => {
        if (!f.key.startsWith(currentPrefix.value)) return false
        const rest = f.key.slice(currentPrefix.value.length)
        return !rest.includes('/')
      })
    : allFiles.value
  if (q) {
    files = files.filter((f) => f.key.toLowerCase().includes(q))
  }
  return files
})

const displayItems = computed(() => [...folders.value, ...filteredFiles.value])

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      currentPrefix.value = ''
      pickerMode.value = props.initialMode ?? 'file'
      fileStore.setBucket('input')
      await loadFiles()
    }
  },
)

async function loadFiles() {
  await fileStore.fetchFiles('input')
  allFiles.value = [...fileStore.filesByBucket.input]
}

async function refresh() {
  await loadFiles()
}

function navigateToPrefix(prefix: string) {
  currentPrefix.value = prefix
}

function folderName(prefix: string) {
  const parts = prefix.replace(/\/$/, '').split('/')
  return parts[parts.length - 1] + '/'
}

function fileName(key: string) {
  return key.split('/').pop() || key
}

function selectFolder(prefix: string) {
  emit('select-folder', prefix)
  close()
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
  currentPrefix.value = ''
  emit('close')
}
</script>
