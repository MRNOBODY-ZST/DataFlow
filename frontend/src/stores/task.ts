import { ref } from 'vue'
import { defineStore } from 'pinia'
import { taskApi, type Task } from '@/api/task'
import { useAuthStore } from './auth'
import { useNotificationStore } from './notification'

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
    const notify = useNotificationStore()
    notify.add('info', `Task #${data.id}`, `Pipeline ${pipelineId} submitted`)
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
      if (data.status === 'SUCCESS' || data.status === 'FAILED' || data.status === 'CANCELLED') {
        const notify = useNotificationStore()
        if (data.status === 'SUCCESS') {
          notify.add('success', `Task #${taskId}`, data.message || 'Completed successfully')
        } else if (data.status === 'CANCELLED') {
          notify.add('info', `Task #${taskId}`, data.message || 'Task cancelled')
        } else {
          notify.add('error', `Task #${taskId}`, data.message || 'Task failed')
        }
        source.close()
      }
    })

    source.onerror = () => source.close()

    return () => source.close()
  }

  async function cancelTask(id: number) {
    const { data } = await taskApi.cancel(id)
    const idx = tasks.value.findIndex((t) => t.id === id)
    if (idx !== -1) tasks.value[idx] = data
    const notify = useNotificationStore()
    notify.add('info', `Task #${id}`, 'Task cancelled')
    return data
  }

  async function deleteTask(id: number) {
    await taskApi.remove(id)
    tasks.value = tasks.value.filter((t) => t.id !== id)
    const notify = useNotificationStore()
    notify.add('info', `Task #${id}`, 'Task deleted')
  }

  return { tasks, loading, fetchAll, submit, subscribeProgress, cancelTask, deleteTask }
})
