<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-4">
      <router-link to="/tasks" class="text-sm text-gray-500 hover:text-indigo-600">← 任务列表</router-link>
      <span class="font-semibold text-gray-800">任务详情 #{{ id }}</span>
    </nav>

    <main class="max-w-2xl mx-auto px-6 py-8 space-y-6">
      <div v-if="!task" class="text-gray-400">加载中...</div>
      <template v-else>
        <!-- Status card -->
        <div class="bg-white rounded-xl border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-gray-800">执行状态</h3>
            <span class="text-2xl">{{ statusIcon(task.status) }}</span>
          </div>
          <div class="w-full bg-gray-100 rounded-full h-3 mb-2">
            <div
              class="h-3 rounded-full transition-all duration-500"
              :class="task.status === 'FAILED' ? 'bg-red-400' : 'bg-indigo-500'"
              :style="{ width: `${task.progress}%` }"
            />
          </div>
          <p class="text-sm text-gray-500">{{ task.progress }}% · {{ task.status }}</p>
          <p v-if="task.errorMsg" class="mt-3 text-sm text-red-600 bg-red-50 rounded p-2">{{ task.errorMsg }}</p>
        </div>

        <!-- Info -->
        <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-3 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-500">流水线</span>
            <span class="text-gray-800">{{ task.pipelineId }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">输入文件</span>
            <span class="text-gray-800 truncate max-w-48">{{ task.inputPath }}</span>
          </div>
          <div v-if="task.outputPath" class="flex justify-between items-center">
            <span class="text-gray-500">输出文件</span>
            <button class="text-indigo-600 hover:underline text-sm" @click="downloadResult">下载结果</button>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">创建时间</span>
            <span class="text-gray-800">{{ new Date(task.createdAt).toLocaleString() }}</span>
          </div>
          <div v-if="task.finishedAt" class="flex justify-between">
            <span class="text-gray-500">完成时间</span>
            <span class="text-gray-800">{{ new Date(task.finishedAt).toLocaleString() }}</span>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
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
    unsubscribe = taskStore.subscribeProgress(Number(props.id), (e) => {
      if (task.value) {
        task.value.progress = e.progress
        task.value.status = e.status as any
      }
    })
  }
})

onUnmounted(() => unsubscribe?.())

async function downloadResult() {
  if (!task.value?.outputPath) return
  const { url } = await fileApi.presignDownload(task.value.outputPath, 'output')
  window.open(url, '_blank')
}

function statusIcon(s: string) {
  return { PENDING: '⏳', RUNNING: '⚡', SUCCESS: '✅', FAILED: '❌' }[s] ?? '❓'
}
</script>
