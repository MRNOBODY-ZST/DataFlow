<template>
  <AppLayout :title="t('task.title')">
    <div class="py-6 px-4 sm:px-6 lg:px-8">
      <div class="sm:flex sm:items-center sm:justify-between">
        <div>
          <h2 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('task.title') }}</h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('task.description') }}</p>
        </div>
      </div>

      <div class="mt-6 overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-gray-200 dark:bg-gray-800/75 dark:ring-white/10">
        <div v-if="taskStore.loading" class="px-6 py-16 text-center text-sm text-gray-500 dark:text-gray-400">{{ t('common.loading') }}</div>
        <div v-else-if="taskStore.tasks.length === 0" class="px-6 py-16 text-center text-sm text-gray-500 dark:text-gray-400">{{ t('task.noTasks') }}</div>
        <ul v-else role="list" class="divide-y divide-gray-200 dark:divide-white/10">
          <li
            v-for="task in taskStore.tasks"
            :key="task.id"
            class="flex cursor-pointer flex-col gap-4 px-4 py-4 hover:bg-gray-50 sm:flex-row sm:items-center sm:justify-between sm:px-6 dark:hover:bg-white/5"
            @click="openTask(task.id)"
          >
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-gray-900 dark:text-white">{{ t('task.taskId', { id: task.id }) }}</p>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('task.pipelineId', { id: task.pipelineId }) }} · {{ formatTime(task.createdAt) }}</p>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-32">
                <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>{{ t('task.progress') }}</span>
                  <span>{{ task.progress }}%</span>
                </div>
                <div class="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div class="h-2 rounded-full transition-all" :class="progressBarClass(task.status)" :style="{ width: `${task.progress}%` }" />
                </div>
              </div>
              <span class="inline-flex items-center rounded-full px-2 py-1 text-xs font-medium" :class="statusClass(task.status)">{{ statusLabel(task.status) }}</span>
              <button
                v-if="task.status === 'PENDING' || task.status === 'RUNNING'"
                type="button"
                class="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-amber-600 dark:hover:bg-white/10 dark:hover:text-amber-400"
                :title="t('task.cancelTask')"
                @click.stop="handleCancel(task.id)"
              >
                <XMarkIcon class="size-4" />
              </button>
              <button
                v-if="task.status === 'SUCCESS' || task.status === 'FAILED' || task.status === 'CANCELLED'"
                type="button"
                class="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-red-600 dark:hover:bg-white/10 dark:hover:text-red-400"
                :title="t('task.deleteTask')"
                @click.stop="handleDelete(task.id)"
              >
                <TrashIcon class="size-4" />
              </button>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <TaskDetailModal :open="detailOpen" :task-id="selectedTaskId" @close="detailOpen = false" />
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { XMarkIcon, TrashIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/layout/AppLayout.vue'
import TaskDetailModal from '@/components/task/TaskDetailModal.vue'
import { useTaskStore } from '@/stores/task'

const { t } = useI18n()
const taskStore = useTaskStore()

const detailOpen = ref(false)
const selectedTaskId = ref<number | null>(null)
const sseUnsubs = new Map<number, () => void>()

const activeTasks = computed(() =>
  taskStore.tasks.filter((t) => t.status === 'RUNNING' || t.status === 'PENDING'),
)

function subscribeActive() {
  for (const task of activeTasks.value) {
    if (sseUnsubs.has(task.id)) continue
    const unsub = taskStore.subscribeProgress(task.id, () => {})
    sseUnsubs.set(task.id, unsub)
  }
  for (const [id, unsub] of sseUnsubs) {
    if (!activeTasks.value.some((t) => t.id === id)) {
      unsub()
      sseUnsubs.delete(id)
    }
  }
}

watch(activeTasks, subscribeActive, { deep: true })

onMounted(async () => {
  await taskStore.fetchAll()
  subscribeActive()
})

onUnmounted(() => {
  for (const unsub of sseUnsubs.values()) unsub()
  sseUnsubs.clear()
})

function openTask(id: number) {
  selectedTaskId.value = id
  detailOpen.value = true
}

async function handleCancel(id: number) {
  if (!confirm(t('task.confirmCancel'))) return
  await taskStore.cancelTask(id)
}

async function handleDelete(id: number) {
  if (!confirm(t('task.confirmDelete'))) return
  await taskStore.deleteTask(id)
}

function formatTime(iso: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false,
  })
}

function statusClass(status: string) {
  return {
    PENDING: 'bg-gray-100 text-gray-700 dark:bg-gray-400/10 dark:text-gray-400',
    RUNNING: 'bg-blue-100 text-blue-700 dark:bg-blue-400/10 dark:text-blue-400',
    SUCCESS: 'bg-green-100 text-green-700 dark:bg-green-400/10 dark:text-green-400',
    FAILED: 'bg-red-100 text-red-700 dark:bg-red-400/10 dark:text-red-400',
    CANCELLED: 'bg-amber-100 text-amber-700 dark:bg-amber-400/10 dark:text-amber-400',
  }[status] || 'bg-gray-100 text-gray-700 dark:bg-gray-400/10 dark:text-gray-400'
}

function progressBarClass(status: string) {
  if (status === 'FAILED') return 'bg-red-400'
  if (status === 'CANCELLED') return 'bg-amber-400'
  return 'bg-sky-600 dark:bg-sky-500'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    PENDING: t('task.pending'),
    RUNNING: t('task.running'),
    SUCCESS: t('task.success'),
    FAILED: t('task.failed'),
    CANCELLED: t('task.cancelled'),
  }
  return map[status] || status
}
</script>
