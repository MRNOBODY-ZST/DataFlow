<template>
  <AppLayout :title="`Task #${id}`">
    <div class="py-6 px-4 sm:px-6 lg:px-8">
      <div v-if="!task" class="rounded-lg bg-white px-6 py-16 text-center text-sm text-gray-500 shadow-sm ring-1 ring-gray-200 dark:bg-gray-800/75 dark:text-gray-400 dark:ring-white/10">Loading...</div>
      <div v-else class="space-y-6">
        <!-- Status card -->
        <div class="rounded-lg bg-white p-6 shadow-sm ring-1 ring-gray-200 dark:bg-gray-800/75 dark:ring-white/10">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-base font-semibold text-gray-900 dark:text-white">Execution Status</h2>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ task.status }}</p>
            </div>
            <span class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium" :class="statusClass(task.status)">{{ task.status }}</span>
          </div>
          <div class="mt-4">
            <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
              <span>Progress</span>
              <span>{{ task.progress }}%</span>
            </div>
            <div class="mt-2 h-3 rounded-full bg-gray-200 dark:bg-gray-700">
              <div class="h-3 rounded-full transition-all" :class="task.status === 'FAILED' ? 'bg-red-400' : 'bg-indigo-600 dark:bg-indigo-500'" :style="{ width: `${task.progress}%` }" />
            </div>
          </div>
          <p v-if="task.errorMsg" class="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-400/10 dark:text-red-400">{{ task.errorMsg }}</p>
        </div>

        <!-- Info card -->
        <div class="overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-gray-200 dark:bg-gray-800/75 dark:ring-white/10">
          <div class="border-b border-gray-200 px-4 py-5 sm:px-6 dark:border-white/10">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white">Task Information</h3>
          </div>
          <div class="border-t border-gray-100 dark:border-white/5">
            <dl class="divide-y divide-gray-100 dark:divide-white/5">
              <div class="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">Pipeline</dt>
                <dd class="mt-1 text-sm text-gray-700 sm:col-span-2 sm:mt-0 dark:text-gray-300">{{ task.pipelineId }}</dd>
              </div>
              <div class="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">Input File</dt>
                <dd class="mt-1 break-all text-sm text-gray-700 sm:col-span-2 sm:mt-0 dark:text-gray-300">{{ task.inputPath }}</dd>
              </div>
              <div class="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">Output File</dt>
                <dd class="mt-1 text-sm text-gray-700 sm:col-span-2 sm:mt-0 dark:text-gray-300">
                  <div v-if="task.outputPath" class="flex items-center justify-between gap-4">
                    <span class="break-all">{{ task.outputPath }}</span>
                    <button type="button" class="shrink-0 rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="downloadResult">Download</button>
                  </div>
                  <span v-else class="text-gray-400 dark:text-gray-500">Not generated yet</span>
                </dd>
              </div>
              <div class="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">Created</dt>
                <dd class="mt-1 text-sm text-gray-700 sm:col-span-2 sm:mt-0 dark:text-gray-300">{{ new Date(task.createdAt).toLocaleString() }}</dd>
              </div>
              <div class="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">Finished</dt>
                <dd class="mt-1 text-sm text-gray-700 sm:col-span-2 sm:mt-0 dark:text-gray-300">{{ task.finishedAt ? new Date(task.finishedAt).toLocaleString() : 'In progress' }}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { taskApi, type Task } from '@/api/task'
import { fileApi } from '@/api/file'
import { useTaskStore } from '@/stores/task'

const props = defineProps<{ id: string }>()
const taskStore = useTaskStore()
const task = ref<Task | null>(null)
let unsubscribe: (() => void) | null = null

onMounted(async () => {
  const { data } = await taskApi.get(Number(props.id))
  task.value = data

  if (data.status === 'PENDING' || data.status === 'RUNNING') {
    unsubscribe = taskStore.subscribeProgress(Number(props.id), (event) => {
      if (!task.value) return
      task.value.progress = event.progress
      task.value.status = event.status as Task['status']
      if (event.outputKey) task.value.outputPath = event.outputKey
      if (event.message && event.status === 'FAILED') task.value.errorMsg = event.message
    })
  }
})

onUnmounted(() => unsubscribe?.())

async function downloadResult() {
  if (!task.value?.outputPath) return
  const { url } = await fileApi.presignDownload(task.value.outputPath, 'output')
  window.open(url, '_blank')
}

function statusClass(status: string) {
  return {
    PENDING: 'bg-gray-100 text-gray-700 dark:bg-gray-400/10 dark:text-gray-400',
    RUNNING: 'bg-blue-100 text-blue-700 dark:bg-blue-400/10 dark:text-blue-400',
    SUCCESS: 'bg-green-100 text-green-700 dark:bg-green-400/10 dark:text-green-400',
    FAILED: 'bg-red-100 text-red-700 dark:bg-red-400/10 dark:text-red-400',
  }[status] || 'bg-gray-100 text-gray-700 dark:bg-gray-400/10 dark:text-gray-400'
}
</script>
