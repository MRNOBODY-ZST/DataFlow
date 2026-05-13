<template>
  <div class="min-h-screen bg-gray-50">
    <div class="mx-auto flex max-w-7xl items-center gap-3 px-4 py-4 sm:px-6 lg:px-8">
      <router-link to="/dashboard" class="text-sm text-gray-500 hover:text-indigo-600">← 返回流水线</router-link>
      <span class="truncate text-lg font-semibold text-gray-900">{{ pipeline?.name ?? '加载中...' }}</span>
      <div class="ml-auto flex gap-2">
        <button class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50" :disabled="saving" @click="save">
          {{ saving ? '保存中...' : '保存' }}
        </button>
        <button class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="showRunDialog = true">
          运行
        </button>
      </div>
    </div>

    <div class="flex h-[calc(100vh-72px)] overflow-hidden border-t border-gray-200 bg-white">
      <NodePanel @drag-start="onDragStart" />

      <div class="relative flex-1" @drop="onDrop" @dragover.prevent>
        <VueFlow
          v-model:nodes="nodes"
          v-model:edges="edges"
          :node-types="nodeTypes"
          fit-view-on-init
          @node-click="onNodeClick"
          @pane-click="selectedNode = null"
          @connect="onConnect"
        >
          <Background />
          <Controls />
          <MiniMap />
        </VueFlow>
      </div>

      <NodeConfig v-if="selectedNode" :node="selectedNode" @update="onNodeUpdate" @close="selectedNode = null" />
    </div>
  </div>

  <TransitionRoot as="template" :show="showRunDialog">
    <Dialog class="relative z-20" @close="showRunDialog = false">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity"></div>
      </TransitionChild>
      <div class="fixed inset-0 z-20 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-xl">
              <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <DialogTitle as="h3" class="text-base font-semibold text-gray-900">运行流水线</DialogTitle>
                <div class="mt-4 space-y-4">
                  <p class="text-sm text-gray-600">确认运行此流水线？输入文件已在节点中配置。</p>
                  <p v-if="runError" class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{{ runError }}</p>
                </div>
              </div>
              <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                <button type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 sm:ml-3 sm:w-auto disabled:opacity-60" :disabled="running" @click="run">
                  {{ running ? '提交中...' : '开始运行' }}
                </button>
                <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto" @click="showRunDialog = false">取消</button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, markRaw, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { VueFlow, useVueFlow, type Edge, type Node, type NodeMouseEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'

import NodePanel from '@/components/flow/NodePanel.vue'
import NodeConfig from '@/components/flow/NodeConfig.vue'
import GenericFlowNode from '@/components/flow/nodes/GenericFlowNode.vue'

import { usePipelineStore } from '@/stores/pipeline'
import { useTaskStore } from '@/stores/task'
import { useNodeSchemaStore } from '@/stores/nodeSchema'

const props = defineProps<{ id: string }>()
const router = useRouter()
const pipelineStore = usePipelineStore()
const taskStore = useTaskStore()
const nodeSchemaStore = useNodeSchemaStore()
const { addNodes, screenToFlowCoordinate, addEdges } = useVueFlow()

const pipeline = ref<any>(null)
const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])
const selectedNode = ref<Node | null>(null)
const saving = ref(false)
const showRunDialog = ref(false)
const running = ref(false)
const runError = ref('')

const nodeTypes = computed(() => {
  const map: Record<string, any> = { default: markRaw(GenericFlowNode) }
  for (const schema of nodeSchemaStore.schemas) {
    map[schema.type] = markRaw(GenericFlowNode)
  }
  return map
})

let dragNodeType = ''

onMounted(async () => {
  await nodeSchemaStore.fetch()
  pipeline.value = await pipelineStore.fetchOne(Number(props.id))
  nodes.value = (pipeline.value.nodes ?? []) as Node[]
  edges.value = (pipeline.value.edges ?? []) as Edge[]
})

function onDragStart(type: string) {
  dragNodeType = type
}

function onDrop(event: DragEvent) {
  if (!dragNodeType) return
  const position = screenToFlowCoordinate({ x: event.clientX, y: event.clientY })
  const schema = nodeSchemaStore.byType[dragNodeType]
  const newNode: Node = {
    id: `${dragNodeType}_${Date.now()}`,
    type: dragNodeType,
    position,
    data: { label: schema?.label ?? dragNodeType },
  }
  addNodes([newNode])
  dragNodeType = ''
}

function onNodeClick({ node }: NodeMouseEvent) {
  selectedNode.value = node
}

function onNodeUpdate(updated: Node) {
  const idx = nodes.value.findIndex((n) => n.id === updated.id)
  if (idx !== -1) nodes.value[idx] = { ...nodes.value[idx], ...updated }
  selectedNode.value = updated
}

function onConnect(connection: any) {
  addEdges([connection])
}

async function save() {
  saving.value = true
  try {
    await pipelineStore.saveGraph(Number(props.id), nodes.value, edges.value)
  } finally {
    saving.value = false
  }
}

async function run() {
  running.value = true
  runError.value = ''
  try {
    await save()
    const task = await taskStore.submit(Number(props.id))
    showRunDialog.value = false
    router.push(`/tasks/${task.id}`)
  } catch (e: any) {
    runError.value = e.message || '任务提交失败'
  } finally {
    running.value = false
  }
}
</script>
