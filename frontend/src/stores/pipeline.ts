import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { pipelineApi, type Pipeline } from '@/api/pipeline'
import type { Node, Edge } from '@vue-flow/core'

export const usePipelineStore = defineStore('pipeline', () => {
  const pipelines: Ref<Pipeline[]> = ref([])
  const current: Ref<Pipeline | null> = ref(null)
  const loading = ref(false)

  async function fetchAll(): Promise<void> {
    loading.value = true
    const response = await pipelineApi.list()
    pipelines.value = response.data as Pipeline[]
    loading.value = false
  }

  async function fetchOne(id: number): Promise<Pipeline> {
    const response = await pipelineApi.get(id)
    const currentPipeline = response.data as Pipeline
    current.value = currentPipeline
    return currentPipeline
  }

  async function createPipeline(name: string, description = ''): Promise<Pipeline> {
    const response = await pipelineApi.create({
      name,
      description,
      nodes: [] as unknown as Node[],
      edges: [] as unknown as Edge[],
    })
    const created = response.data as Pipeline
    pipelines.value = [created, ...pipelines.value]
    return created
  }

  async function saveGraph(id: number, nodes: Node[], edges: Edge[]): Promise<Pipeline> {
    const response = await pipelineApi.update(id, { nodes, edges })
    const updated = response.data as Pipeline
    current.value = updated
    return updated
  }

  async function deletePipeline(id: number): Promise<void> {
    await pipelineApi.delete(id)
    pipelines.value = pipelines.value.filter((pipeline) => pipeline.id !== id)
  }

  return { pipelines, current, loading, fetchAll, fetchOne, createPipeline, saveGraph, deletePipeline }
})
