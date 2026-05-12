<template>
  <div class="h-screen flex flex-col bg-gray-100">
    <!-- Top bar -->
    <div class="bg-white border-b border-gray-200 px-4 py-2 flex items-center gap-3 shrink-0">
      <router-link to="/dashboard" class="text-sm text-gray-500 hover:text-indigo-600">← 返回</router-link>
      <span class="font-semibold text-gray-800 truncate">{{ pipeline?.name ?? '加载中...' }}</span>
      <div class="ml-auto flex gap-2">
        <button
          class="text-sm px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          :disabled="saving"
          @click="save"
        >
          {{ saving ? '保存中...' : '保存' }}
        </button>
        <button
          class="text-sm px-3 py-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition"
          @click="showRunDialog = true"
        >
          ▶ 运行
        </button>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <!-- Left: node palette -->
      <NodePanel @drag-start="onDragStart" />

      <!-- Center: flow canvas -->
      <div class="flex-1 relative" @drop="onDrop" @dragover.prevent>
        <VueFlow
          v-model:nodes="nodes"
          v-model:edges="edges"
          :node-types="nodeTypes"
          fit-view-on-init
          @node-click="onNodeClick"
          @pane-click="selectedNode = null"
        >
          <Background />
          <Controls />
          <MiniMap />
        </VueFlow>
      </div>

      <!-- Right: config drawer -->
      <NodeConfig v-if="selectedNode" :node="selectedNode" @update="onNodeUpdate" @close="selectedNode = null" />
    </div>

    <!-- Run dialog -->
    <div v-if="showRunDialog" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
        <h3 class="text-lg font-semibold mb-4">运行流水线</h3>
        <div class="space-y-3">
          <label class="block text-sm font-medium text-gray-700">选择输入文件</label>
          <input type="file" ref="fileInput" class="text-sm" />
          <p v-if="uploadStatus" class="text-xs text-gray-500">{{ uploadStatus }}</p>
        </div>
        <div class="flex justify-end gap-2 pt-4">
          <button class="text-sm text-gray-500" @click="showRunDialog = false">取消</button>
          <button
            class="bg-indigo-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-indigo-500"
            :disabled="running"
            @click="run"
          >
            {{ running ? '提交中...' : '开始运行' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { VueFlow, useVueFlow, type Node, type Edge, type NodeMouseEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'

import NodePanel from '@/components/flow/NodePanel.vue'
import NodeConfig from '@/components/flow/NodeConfig.vue'
import CsvReaderNode from '@/components/flow/nodes/CsvReaderNode.vue'
import FilterNode from '@/components/flow/nodes/FilterNode.vue'
import ImageResizeNode from '@/components/flow/nodes/ImageResizeNode.vue'
import OutputNode from '@/components/flow/nodes/OutputNode.vue'
import DefaultFlowNode from '@/components/flow/nodes/DefaultFlowNode.vue'

import { usePipelineStore } from '@/stores/pipeline'
import { useTaskStore } from '@/stores/task'
import { fileApi } from '@/api/file'

const props = defineProps<{ id: string }>()
const router = useRouter()
const pipelineStore = usePipelineStore()
const taskStore = useTaskStore()
const { addNodes, addEdges, screenToFlowCoordinate } = useVueFlow()

const pipeline = ref<any>(null)
const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])
const selectedNode = ref<Node | null>(null)
const saving = ref(false)
const showRunDialog = ref(false)
const running = ref(false)
const uploadStatus = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

const nodeTypes = {
  csv_reader: markRaw(CsvReaderNode),
  filter: markRaw(FilterNode),
  image_resize: markRaw(ImageResizeNode),
  minio_writer: markRaw(OutputNode),
  default: markRaw(DefaultFlowNode),
}

let dragNodeType = ''

onMounted(async () => {
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
  const newNode: Node = {
    id: `${dragNodeType}_${Date.now()}`,
    type: dragNodeType,
    position,
    data: { label: dragNodeType },
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

async function save() {
  saving.value = true
  try {
    await pipelineStore.saveGraph(Number(props.id), nodes.value, edges.value)
  } finally {
    saving.value = false
  }
}

async function run() {
  const file = fileInput.value?.files?.[0]
  if (!file) { alert('请选择文件'); return }
  running.value = true
  uploadStatus.value = '正在获取上传地址...'
  try {
    await save()
    const { url, key } = await fileApi.presignUpload(file.name)
    uploadStatus.value = '正在上传文件...'
    await fileApi.uploadToMinio(url, file)
    uploadStatus.value = '正在提交任务...'
    const task = await taskStore.submit(Number(props.id), key)
    showRunDialog.value = false
    router.push(`/tasks/${task.id}`)
  } catch (e: any) {
    uploadStatus.value = `错误: ${e.message}`
  } finally {
    running.value = false
  }
}
</script>
