<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-50" @close="$emit('close')">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="" leave="ease-in duration-200" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50" />
      </TransitionChild>

      <div class="fixed inset-0 z-50 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to=" translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from=" translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative w-full max-w-lg transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
              <div v-if="!task" class="px-6 py-16 text-center text-sm text-gray-500 dark:text-gray-400">{{ t('common.loading') }}</div>
              <template v-else>
                <!-- Header -->
                <div class="px-6 pt-5 pb-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <DialogTitle class="text-base font-semibold text-gray-900 dark:text-white">{{ t('task.taskId', { id: task.id }) }}</DialogTitle>
                      <p class="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{{ t('task.pipelineId', { id: task.pipelineId }) }}</p>
                    </div>
                    <span class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium" :class="statusClass(task.status)">{{ task.status }}</span>
                  </div>

                  <!-- Progress -->
                  <div class="mt-4">
                    <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span>{{ t('task.progress') }}</span>
                      <span>{{ task.progress }}%</span>
                    </div>
                    <div class="mt-1.5 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                      <div class="h-2 rounded-full transition-all" :class="task.status === 'FAILED' ? 'bg-red-400' : 'bg-indigo-600 dark:bg-indigo-500'" :style="{ width: `${task.progress}%` }" />
                    </div>
                  </div>

                  <p v-if="task.errorMsg" class="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-400/10 dark:text-red-400">{{ task.errorMsg }}</p>
                </div>

                <!-- Info -->
                <div class="border-t border-gray-100 dark:border-white/5">
                  <dl class="divide-y divide-gray-100 dark:divide-white/5">
                    <div v-if="task.outputPath" class="px-6 py-3 sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('task.output') }}</dt>
                      <dd class="mt-1 sm:col-span-2 sm:mt-0">
                        <div class="flex items-center justify-between gap-3">
                          <span class="break-all text-sm text-gray-700 dark:text-gray-300">{{ task.outputPath }}</span>
                          <button type="button" class="shrink-0 rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="downloadResult">{{ t('common.download') }}</button>
                        </div>
                      </dd>
                    </div>
                    <div class="px-6 py-3 sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('task.created') }}</dt>
                      <dd class="mt-1 text-sm text-gray-700 sm:col-span-2 sm:mt-0 dark:text-gray-300">{{ formatTime(task.createdAt) }}</dd>
                    </div>
                    <div class="px-6 py-3 sm:grid sm:grid-cols-3 sm:gap-4">
                      <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('task.finished') }}</dt>
                      <dd class="mt-1 text-sm text-gray-700 sm:col-span-2 sm:mt-0 dark:text-gray-300">{{ task.finishedAt ? formatTime(task.finishedAt) : t('task.inProgress') }}</dd>
                    </div>
                  </dl>
                </div>

                <!-- Footer -->
                <div class="border-t border-gray-100 px-6 py-3 dark:border-white/5">
                  <button type="button" class="w-full rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="$emit('close')">{{ t('common.close') }}</button>
                </div>
              </template>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { taskApi, type Task } from '@/api/task'
import { fileApi } from '@/api/file'
import { useTaskStore } from '@/stores/task'

const props = defineProps<{ open: boolean; taskId: number | null }>()
defineEmits<{ close: [] }>()

const taskStore = useTaskStore()
const { t } = useI18n()
const task = ref<Task | null>(null)
let unsubscribe: (() => void) | null = null

watch(() => [props.open, props.taskId] as const, async ([isOpen, id]) => {
  if (unsubscribe) { unsubscribe(); unsubscribe = null }
  if (!isOpen || !id) { task.value = null; return }

  const { data } = await taskApi.get(id)
  task.value = data

  if (data.status === 'PENDING' || data.status === 'RUNNING') {
    unsubscribe = taskStore.subscribeProgress(id, (event) => {
      if (!task.value) return
      task.value.progress = event.progress
      task.value.status = event.status as Task['status']
      if (event.outputKey) task.value.outputPath = event.outputKey
      if (event.message && event.status === 'FAILED') task.value.errorMsg = event.message
      if (event.status === 'SUCCESS' || event.status === 'FAILED') {
        task.value.finishedAt = new Date().toISOString()
      }
    })
  }
}, { immediate: true })

onUnmounted(() => unsubscribe?.())

function formatTime(iso: string): string {
  if (!iso) return ''
  const d = iso.includes('T') && !iso.includes('Z') && !iso.includes('+')
    ? new Date(iso)
    : new Date(iso)
  return d.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false,
  })
}

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
