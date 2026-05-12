import http from './http'

export interface Task {
  id: number
  pipelineId: number
  status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED'
  progress: number
  inputPath: string
  outputPath: string | null
  errorMsg: string | null
  createdAt: string
  finishedAt: string | null
}

export const taskApi = {
  submit: (pipelineId: number, inputKey: string) =>
    http.post<Task>('/tasks', { pipelineId, inputKey }),

  list: () => http.get<Task[]>('/tasks'),

  get: (id: number) => http.get<Task>(`/tasks/${id}`),
}
