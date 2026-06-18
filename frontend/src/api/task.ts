import http from './http'

export interface Task {
  id: number
  pipelineId: number
  status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED' | 'CANCELLED'
  progress: number
  inputPath: string
  outputPath: string | null
  errorMsg: string | null
  createdAt: string
  finishedAt: string | null
}

export const taskApi = {
  submit: (pipelineId: number) =>
    http.post<Task>('/tasks', { pipelineId }),

  list: () => http.get<Task[]>('/tasks'),

  get: (id: number) => http.get<Task>(`/tasks/${id}`),

  cancel: (id: number) => http.post<Task>(`/tasks/${id}/cancel`),

  remove: (id: number) => http.delete<void>(`/tasks/${id}`),
}
