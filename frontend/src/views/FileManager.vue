<template>
  <AppNav title="文件管理" description="统一管理上传输入文件和任务输出文件。">
    <template #actions>
      <button
        type="button"
        class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500"
        @click="showUpload = true"
      >
        上传文件
      </button>
    </template>

    <div class="space-y-6">
      <div class="grid gap-4 md:grid-cols-3">
        <div class="rounded-lg bg-white p-5 shadow-sm ring-1 ring-gray-200">
          <dt class="text-sm font-medium text-gray-500">输入文件</dt>
          <dd class="mt-2 text-3xl font-semibold tracking-tight text-gray-900">{{ inputCount }}</dd>
        </div>
        <div class="rounded-lg bg-white p-5 shadow-sm ring-1 ring-gray-200">
          <dt class="text-sm font-medium text-gray-500">输出文件</dt>
          <dd class="mt-2 text-3xl font-semibold tracking-tight text-gray-900">{{ outputCount }}</dd>
        </div>
        <div class="rounded-lg bg-white p-5 shadow-sm ring-1 ring-gray-200">
          <dt class="text-sm font-medium text-gray-500">当前 Bucket</dt>
          <dd class="mt-2 text-3xl font-semibold tracking-tight text-gray-900">{{ fileStore.activeBucket }}</dd>
        </div>
      </div>

      <div class="rounded-lg bg-white shadow-sm ring-1 ring-gray-200">
        <div class="border-b border-gray-200 px-4 py-4 sm:px-6">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <button
                v-for="bucket in buckets"
                :key="bucket"
                type="button"
                class="rounded-full px-3 py-1.5 text-sm font-medium"
                :class="fileStore.activeBucket === bucket ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
                @click="switchBucket(bucket)"
              >
                {{ bucketLabels[bucket] }}
              </button>
            </div>
            <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50" @click="refresh">刷新</button>
          </div>
        </div>

        <div v-if="fileStore.loading" class="px-6 py-16 text-center text-sm text-gray-500">加载中...</div>
        <div v-else-if="fileStore.files.length === 0" class="px-6 py-16 text-center">
          <div class="mx-auto max-w-sm rounded-lg border border-dashed border-gray-300 px-6 py-10">
            <FolderIcon class="mx-auto size-10 text-gray-400" />
            <h3 class="mt-2 text-sm font-semibold text-gray-900">当前没有文件</h3>
            <p class="mt-1 text-sm text-gray-500">先上传一个文件，随后可在节点配置和运行弹窗中直接选择。</p>
            <div class="mt-6">
              <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="showUpload = true">上传文件</button>
            </div>
          </div>
        </div>
        <ul v-else role="list" class="divide-y divide-gray-200">
          <li
            v-for="file in fileStore.files"
            :key="file.key"
            class="flex flex-col gap-4 px-4 py-4 hover:bg-gray-50 sm:flex-row sm:items-center sm:justify-between sm:px-6"
          >
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-gray-900">{{ file.key }}</p>
              <div class="mt-2 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                <span>{{ prettySize(file.size) }}</span>
                <span>{{ formatDate(file.lastModified) }}</span>
                <span class="rounded-full bg-gray-100 px-2 py-1 text-gray-600">{{ file.bucket }}</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50" @click="openDetails(file)">查看</button>
              <button
                v-if="file.bucket === 'input'"
                type="button"
                class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-red-600 shadow-xs inset-ring inset-ring-red-200 hover:bg-red-50"
                @click="remove(file)"
              >
                删除
              </button>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </AppNav>

  <UploadModal :open="showUpload" @close="showUpload = false" @uploaded="onUploaded" />
  <FileDetailDrawer :open="showDetails" :file="detailFile" @close="showDetails = false" @deleted="onDeleted" />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { FolderIcon } from '@heroicons/vue/24/outline'
import AppNav from '@/components/ui/AppNav.vue'
import UploadModal from '@/components/ui/UploadModal.vue'
import FileDetailDrawer from '@/components/ui/FileDetailDrawer.vue'
import { useFileStore } from '@/stores/file'
import type { FileBucket, FileMetadata } from '@/api/file'

const fileStore = useFileStore()
const showUpload = ref(false)
const showDetails = ref(false)
const detailFile = ref<FileMetadata | null>(null)

const buckets: FileBucket[] = ['input', 'output', 'temp']
const bucketLabels: Record<FileBucket, string> = {
  input: '输入',
  output: '输出',
  temp: '临时',
}

const inputCount = computed(() => fileStore.filesByBucket.input.length)
const outputCount = computed(() => fileStore.filesByBucket.output.length)

onMounted(async () => {
  await fileStore.fetchFiles('input')
})

async function switchBucket(bucket: FileBucket) {
  fileStore.setBucket(bucket)
  await fileStore.fetchFiles(bucket)
}

async function refresh() {
  await fileStore.fetchFiles(fileStore.activeBucket)
}

function openDetails(file: FileMetadata) {
  detailFile.value = file
  showDetails.value = true
}

async function remove(file: FileMetadata) {
  await fileStore.deleteFile(file.bucket, file.key)
}

async function onUploaded(file: FileMetadata) {
  showUpload.value = false
  fileStore.filesByBucket.input.unshift(file)
  fileStore.setBucket('input')
  await fileStore.fetchFiles('input')
}

async function onDeleted(file: FileMetadata) {
  await fileStore.deleteFile(file.bucket, file.key)
  showDetails.value = false
  detailFile.value = null
}

function prettySize(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}
</script>
