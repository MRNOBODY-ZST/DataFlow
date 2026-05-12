import { ref } from 'vue'
import { defineStore } from 'pinia'
import { pipelineApi, type Pipeline } from '@/api/pipeline'
import type { Node, Edge } from '@vue-flow/core'

export const usePipelineStore = defineStore('pipeline', () => {
  const pipelines = ref<Pipeline[]>([])
  const current = ref<Pipeline | null>(null)
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    const { data } = await pipelineApi.list()
    pipelines.value = data
    loading.value = false
  }

  async function fetchOne(id: number) {
    const { data } = await pipelineApi.get(id)
    current.value = data
    return data
  }

  async function createPipeline(name: string, description = '') {
    const { data } = await pipelineApi.create({ name, description, nodes: [], edges: [] })
    pipelines.value.unshift(data)
    return data
  }

  async function saveGraph(id: number, nodes: Node[], edges: Edge[]) {
    const { data } = await pipelineApi.update(id, { nodes: nodes as any, edges: edges as any })
    current.value = data
    return data
  }

  async function deletePipeline(id: number) {
    await pipelineApi.delete(id)
    pipelines.value = pipelines.value.filter((p) => p.id !== id)
  }

  return { pipelines, current, loading, fetchAll, fetchOne, createPipeline, saveGraph, deletePipeline }
})
