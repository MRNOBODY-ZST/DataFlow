import { ref } from 'vue'
import { defineStore } from 'pinia'
import { taskApi, type Task } from '@/api/task'
import { useAuthStore } from './auth'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    const { data } = await taskApi.list()
    tasks.value = data
    loading.value = false
  }

  async function submit(pipelineId: number): Promise<Task> {
    const { data } = await taskApi.submit(pipelineId)
    tasks.value.unshift(data)
    return data
  }

  function subscribeProgress(
    taskId: number,
    onEvent: (e: { progress: number; status: string; message?: string; outputKey?: string | null }) => void,
  ): () => void {
    const auth = useAuthStore()
    const url = auth.token
      ? `/api/tasks/${taskId}/progress?token=${encodeURIComponent(auth.token)}`
      : `/api/tasks/${taskId}/progress`
    const source = new EventSource(url)

    source.addEventListener('progress', (e) => {
      const data = JSON.parse((e as MessageEvent).data)
      onEvent(data)
      const task = tasks.value.find((t) => t.id === taskId)
      if (task) {
        task.progress = data.progress
        task.status = data.status
        if (data.outputKey) {
          task.outputPath = data.outputKey
        }
        if (data.status === 'FAILED' && data.message) {
          task.errorMsg = data.message
        }
      }
      if (data.status === 'SUCCESS' || data.status === 'FAILED') {
        source.close()
      }
    })

    source.onerror = () => source.close()

    return () => source.close()
  }

  return { tasks, loading, fetchAll, submit, subscribeProgress }
})
