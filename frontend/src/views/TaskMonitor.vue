<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-4">
      <router-link to="/dashboard" class="text-sm text-gray-500 hover:text-indigo-600">← 流水线</router-link>
      <span class="font-semibold text-gray-800">任务监控</span>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-8">
      <div v-if="taskStore.loading" class="text-center text-gray-400 py-16">加载中...</div>
      <div v-else-if="taskStore.tasks.length === 0" class="text-center text-gray-400 py-16">暂无任务</div>
      <div v-else class="space-y-3">
        <div
          v-for="t in taskStore.tasks"
          :key="t.id"
          class="bg-white rounded-xl border border-gray-200 px-5 py-4 flex items-center gap-4 cursor-pointer hover:shadow-sm transition"
          @click="router.push(`/tasks/${t.id}`)"
        >
          <span class="text-xl">{{ statusIcon(t.status) }}</span>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-800">任务 #{{ t.id }}</p>
            <p class="text-xs text-gray-500">流水线 {{ t.pipelineId }} · {{ new Date(t.createdAt).toLocaleString() }}</p>
          </div>
          <div class="text-right shrink-0">
            <span
              class="inline-block text-xs px-2 py-0.5 rounded-full font-medium"
              :class="statusClass(t.status)"
            >
              {{ t.status }}
            </span>
            <div class="mt-1 w-24 bg-gray-200 rounded-full h-1.5">
              <div
                class="h-1.5 rounded-full transition-all"
                :class="t.status === 'FAILED' ? 'bg-red-400' : 'bg-indigo-500'"
                :style="{ width: `${t.progress}%` }"
              />
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskStore } from '@/stores/task'

const router = useRouter()
const taskStore = useTaskStore()

onMounted(() => taskStore.fetchAll())

function statusIcon(s: string) {
  return { PENDING: '⏳', RUNNING: '⚡', SUCCESS: '✅', FAILED: '❌' }[s] ?? '❓'
}
function statusClass(s: string) {
  return {
    PENDING: 'bg-gray-100 text-gray-600',
    RUNNING: 'bg-blue-100 text-blue-700',
    SUCCESS: 'bg-green-100 text-green-700',
    FAILED:  'bg-red-100 text-red-700',
  }[s] ?? ''
}
</script>
