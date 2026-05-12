import http from './http'
import type { Node, Edge } from '@vue-flow/core'

export interface Pipeline {
  id: number
  name: string
  description: string
  graphId: string
  nodes: Node[]
  edges: Edge[]
  createdAt: string
  updatedAt: string
}

export const pipelineApi = {
  list: () => http.get<Pipeline[]>('/pipelines'),

  get: (id: number) => http.get<Pipeline>(`/pipelines/${id}`),

  create: (data: { name: string; description?: string; nodes?: Node[]; edges?: Edge[] }) =>
    http.post<Pipeline>('/pipelines', data),

  update: (id: number, data: { name?: string; description?: string; nodes?: Node[]; edges?: Edge[] }) =>
    http.put<Pipeline>(`/pipelines/${id}`, data),

  delete: (id: number) => http.delete(`/pipelines/${id}`),
}
