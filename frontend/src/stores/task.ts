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

  async function submit(pipelineId: number, inputKey: string): Promise<Task> {
    const { data } = await taskApi.submit(pipelineId, inputKey)
    tasks.value.unshift(data)
    return data
  }

  function subscribeProgress(taskId: number, onEvent: (e: { progress: number; status: string; message?: string }) => void): () => void {
    const auth = useAuthStore()
    const url = `/api/tasks/${taskId}/progress`
    const source = new EventSource(url)

    source.addEventListener('progress', (e) => {
      const data = JSON.parse(e.data)
      onEvent(data)
      // sync local state
      const task = tasks.value.find((t) => t.id === taskId)
      if (task) {
        task.progress = data.progress
        task.status = data.status
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
