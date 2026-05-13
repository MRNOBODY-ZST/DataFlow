<template>
  <AppLayout title="Tasks">
    <div class="py-6 px-4 sm:px-6 lg:px-8">
      <div class="sm:flex sm:items-center sm:justify-between">
        <div>
          <h2 class="text-base font-semibold text-gray-900 dark:text-white">Task Monitor</h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">View task history and real-time progress.</p>
        </div>
      </div>

      <div class="mt-6 overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-gray-200 dark:bg-gray-800/75 dark:ring-white/10">
        <div v-if="taskStore.loading" class="px-6 py-16 text-center text-sm text-gray-500 dark:text-gray-400">Loading...</div>
        <div v-else-if="taskStore.tasks.length === 0" class="px-6 py-16 text-center text-sm text-gray-500 dark:text-gray-400">No tasks yet</div>
        <ul v-else role="list" class="divide-y divide-gray-200 dark:divide-white/10">
          <li
            v-for="task in taskStore.tasks"
            :key="task.id"
            class="flex flex-col gap-4 px-4 py-4 hover:bg-gray-50 sm:flex-row sm:items-center sm:justify-between sm:px-6 dark:hover:bg-white/5"
          >
            <div class="min-w-0 cursor-pointer" @click="router.push(`/tasks/${task.id}`)">
              <p class="truncate text-sm font-semibold text-gray-900 dark:text-white">Task #{{ task.id }}</p>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Pipeline {{ task.pipelineId }} · {{ new Date(task.createdAt).toLocaleString() }}</p>
            </div>
            <div class="flex items-center gap-4">
              <div class="w-32">
                <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>Progress</span>
                  <span>{{ task.progress }}%</span>
                </div>
                <div class="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div class="h-2 rounded-full transition-all" :class="task.status === 'FAILED' ? 'bg-red-400' : 'bg-indigo-600 dark:bg-indigo-500'" :style="{ width: `${task.progress}%` }" />
                </div>
              </div>
              <span class="inline-flex items-center rounded-full px-2 py-1 text-xs font-medium" :class="statusClass(task.status)">{{ task.status }}</span>
              <button type="button" class="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="router.push(`/tasks/${task.id}`)">View</button>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useTaskStore } from '@/stores/task'

const router = useRouter()
const taskStore = useTaskStore()
let timer: number | null = null

const hasRunningTask = computed(() => taskStore.tasks.some((task) => task.status === 'RUNNING' || task.status === 'PENDING'))

onMounted(async () => {
  await taskStore.fetchAll()
  timer = window.setInterval(() => {
    if (hasRunningTask.value) {
      taskStore.fetchAll()
    }
  }, 10000)
})

onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})

function statusClass(status: string) {
  return {
    PENDING: 'bg-gray-100 text-gray-700 dark:bg-gray-400/10 dark:text-gray-400',
    RUNNING: 'bg-blue-100 text-blue-700 dark:bg-blue-400/10 dark:text-blue-400',
    SUCCESS: 'bg-green-100 text-green-700 dark:bg-green-400/10 dark:text-green-400',
    FAILED: 'bg-red-100 text-red-700 dark:bg-red-400/10 dark:text-red-400',
  }[status] || 'bg-gray-100 text-gray-700 dark:bg-gray-400/10 dark:text-gray-400'
}
</script>
