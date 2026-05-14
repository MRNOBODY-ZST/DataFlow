<template>
  <AppLayout title="">
    <div class="flex h-[calc(100vh-4rem)] flex-col bg-gray-50 dark:bg-gray-900">
      <!-- Top bar -->
      <div class="flex h-14 shrink-0 items-center gap-3 border-b border-gray-200 bg-white px-4 shadow-xs sm:px-6 dark:border-white/10 dark:bg-gray-900 dark:shadow-none">
        <router-link to="/pipelines" class="text-sm text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400">
          <ArrowLeftIcon class="size-5" />
        </router-link>
        <span class="truncate text-sm font-semibold text-gray-900 dark:text-white">{{ pipeline?.name ?? t('common.loading') }}</span>
        <div class="ml-auto flex items-center gap-2">
          <!-- Save status indicator -->
          <transition enter-active-class="transition ease-out duration-200" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100" leave-active-class="transition ease-in duration-150" leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
            <span v-if="saveStatus === 'saved'" class="flex items-center gap-1 text-xs font-medium text-green-600 dark:text-green-400">
              <CheckCircleIcon class="size-4" />
              {{ t('editor.saved') }}
            </span>
            <span v-else-if="saveStatus === 'error'" class="flex items-center gap-1 text-xs font-medium text-red-600 dark:text-red-400">
              <ExclamationCircleIcon class="size-4" />
              {{ t('editor.error') }}
            </span>
          </transition>
          <button class="rounded-md bg-white px-3 py-1.5 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" :disabled="saving" @click="save">
            {{ saving ? t('editor.saving') : t('editor.save') }}
          </button>
          <button class="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="showRunDialog = true">
            {{ t('editor.run') }}
          </button>
          <button class="rounded-md bg-white px-3 py-1.5 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="drawerOpen = !drawerOpen">
            <Squares2X2Icon class="size-5" />
          </button>
        </div>
      </div>

      <!-- Canvas + Drawer container -->
      <div class="relative flex-1 overflow-hidden" @drop="onDrop" @dragover.prevent>
        <VueFlow
          v-model:nodes="nodes"
          v-model:edges="edges"
          :node-types="nodeTypes"
          :edge-types="edgeTypes"
          :delete-key-code="['Delete', 'Backspace']"
          @node-double-click="onNodeDoubleClick"
          @pane-click="selectedNode = null"
          @connect="onConnect"
        >
          <Background />
          <Controls />
          <MiniMap />
        </VueFlow>

        <!-- Node Drawer (right side, inside canvas area) -->
        <NodeDrawer :open="drawerOpen" @close="drawerOpen = false" @drag-start="onDragStart" />
      </div>

      <!-- Node Config Modal -->
      <NodeConfigModal :open="configOpen" :node="selectedNode" @update="onNodeUpdate" @close="configOpen = false" />

      <!-- Run Dialog -->
      <TransitionRoot as="template" :show="showRunDialog">
        <Dialog class="relative z-50" @close="showRunDialog = false">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="" leave="ease-in duration-200" leave-from="" leave-to="opacity-0">
            <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50"></div>
          </TransitionChild>
          <div class="fixed inset-0 z-50 w-screen overflow-y-auto">
            <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
              <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to=" translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from=" translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
                <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6 dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
                  <div>
                    <div class="mx-auto flex size-12 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-500/10">
                      <PlayIcon class="size-6 text-indigo-600 dark:text-indigo-400" aria-hidden="true" />
                    </div>
                    <div class="mt-3 text-center sm:mt-5">
                      <DialogTitle as="h3" class="text-base font-semibold text-gray-900 dark:text-white">{{ t('editor.runPipeline') }}</DialogTitle>
                      <div class="mt-2">
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('editor.runConfirm') }}</p>
                        <p v-if="runError" class="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-400/10 dark:text-red-400">{{ runError }}</p>
                      </div>
                    </div>
                  </div>
                  <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                    <button type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 sm:col-start-2 disabled:opacity-60 dark:bg-indigo-500 dark:hover:bg-indigo-400" :disabled="running" @click="run">
                      {{ running ? t('editor.submitting') : t('common.start') }}
                    </button>
                    <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0 dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showRunDialog = false">{{ t('common.cancel') }}</button>
                  </div>
                </DialogPanel>
              </TransitionChild>
            </div>
          </div>
        </Dialog>
      </TransitionRoot>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, markRaw, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { VueFlow, useVueFlow, type Edge, type Node, type NodeMouseEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { ArrowLeftIcon, CheckCircleIcon, ExclamationCircleIcon, PlayIcon, Squares2X2Icon } from '@heroicons/vue/24/outline'

import AppLayout from '@/components/layout/AppLayout.vue'
import NodeDrawer from '@/components/flow/NodeDrawer.vue'
import NodeConfigModal from '@/components/flow/NodeConfigModal.vue'
import GenericFlowNode from '@/components/flow/nodes/GenericFlowNode.vue'
import AnimatedDashEdge from '@/components/flow/edges/AnimatedDashEdge.vue'

import { usePipelineStore } from '@/stores/pipeline'
import { useTaskStore } from '@/stores/task'
import { useNodeSchemaStore } from '@/stores/nodeSchema'

const props = defineProps<{ id: string }>()
const { t } = useI18n()
const router = useRouter()
const pipelineStore = usePipelineStore()
const taskStore = useTaskStore()
const nodeSchemaStore = useNodeSchemaStore()
const { addNodes, screenToFlowCoordinate, addEdges, updateNodeData, fitView, onNodesInitialized } = useVueFlow()

const pipeline = ref<any>(null)
const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])
const selectedNode = ref<Node | null>(null)
const saving = ref(false)
const saveStatus = ref<'idle' | 'saved' | 'error'>('idle')
const showRunDialog = ref(false)
const running = ref(false)
const runError = ref('')
const drawerOpen = ref(true)
const configOpen = ref(false)

let saveStatusTimer: ReturnType<typeof setTimeout> | null = null

const nodeTypes = computed(() => {
  const map: Record<string, any> = { default: markRaw(GenericFlowNode) }
  for (const schema of nodeSchemaStore.schemas) {
    map[schema.type] = markRaw(GenericFlowNode)
  }
  return map
})

const edgeTypes = { default: markRaw(AnimatedDashEdge) }

let dragNodeType = ''
let initialLoadDone = false

onNodesInitialized(() => {
  if (!initialLoadDone) {
    initialLoadDone = true
    fitView({ maxZoom: 1, padding: 0 })
  }
})

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
    data: {},
  }
  addNodes([newNode])
  dragNodeType = ''
}

function onNodeDoubleClick({ node }: NodeMouseEvent) {
  selectedNode.value = node
  configOpen.value = true
}

function onNodeUpdate(updated: Node) {
  updateNodeData(updated.id, { ...updated.data })
  const node = nodes.value.find((n) => n.id === updated.id)
  if (node) selectedNode.value = node
}

function onConnect(connection: any) {
  addEdges([connection])
}

function showSaveStatus(status: 'saved' | 'error') {
  saveStatus.value = status
  if (saveStatusTimer) clearTimeout(saveStatusTimer)
  saveStatusTimer = setTimeout(() => {
    saveStatus.value = 'idle'
  }, 2000)
}

async function save() {
  saving.value = true
  try {
    await pipelineStore.saveGraph(Number(props.id), nodes.value, edges.value)
    showSaveStatus('saved')
  } catch {
    showSaveStatus('error')
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
    router.push('/tasks')
  } catch (e: any) {
    runError.value = e.message || 'Failed to submit task'
  } finally {
    running.value = false
  }
}
</script>
