<template>
  <AppNav title="任务监控" description="查看历史任务与运行中的实时进度。">
    <div class="overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-gray-200">
      <div v-if="taskStore.loading" class="px-6 py-16 text-center text-sm text-gray-500">加载中...</div>
      <div v-else-if="taskStore.tasks.length === 0" class="px-6 py-16 text-center text-sm text-gray-500">暂无任务</div>
      <ul v-else role="list" class="divide-y divide-gray-200">
        <li
          v-for="task in taskStore.tasks"
          :key="task.id"
          class="flex flex-col gap-4 px-4 py-4 hover:bg-gray-50 sm:flex-row sm:items-center sm:justify-between sm:px-6"
        >
          <div class="min-w-0 cursor-pointer" @click="router.push(`/tasks/${task.id}`)">
            <p class="truncate text-sm font-semibold text-gray-900">任务 #{{ task.id }}</p>
            <p class="mt-1 text-sm text-gray-500">流水线 {{ task.pipelineId }} · {{ new Date(task.createdAt).toLocaleString() }}</p>
          </div>
          <div class="flex items-center gap-4">
            <div class="w-32">
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span>进度</span>
                <span>{{ task.progress }}%</span>
              </div>
              <div class="mt-1 h-2 rounded-full bg-gray-200">
                <div class="h-2 rounded-full transition-all" :class="task.status === 'FAILED' ? 'bg-red-400' : 'bg-indigo-600'" :style="{ width: `${task.progress}%` }" />
              </div>
            </div>
            <span class="inline-flex items-center rounded-full px-2 py-1 text-xs font-medium" :class="statusClass(task.status)">{{ task.status }}</span>
            <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="router.push(`/tasks/${task.id}`)">查看</button>
          </div>
        </li>
      </ul>
    </div>
  </AppNav>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppNav from '@/components/ui/AppNav.vue'
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
    PENDING: 'bg-gray-100 text-gray-700',
    RUNNING: 'bg-blue-100 text-blue-700',
    SUCCESS: 'bg-green-100 text-green-700',
    FAILED: 'bg-red-100 text-red-700',
  }[status] || 'bg-gray-100 text-gray-700'
}
</script>
