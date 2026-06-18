<template>
  <div class="select-none text-sm">
    <div v-for="item in treeNodes" :key="item.path" class="group">
      <!-- Node row -->
      <div
        class="flex items-center gap-1 rounded px-1.5 py-0.5 transition-colors"
        :class="[
          isDragging === item.path ? 'bg-sky-100 dark:bg-sky-500/20' : 'hover:bg-gray-100 dark:hover:bg-white/5',
          (item.type !== 'object' || !item.hasChildren) ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer',
        ]"
        :style="{ paddingLeft: `${item.depth * 16 + 4}px` }"
        :draggable="item.type !== 'object' || !item.hasChildren"
        @dragstart="onDragStart($event, item)"
        @dragend="isDragging = ''"
        @click="toggle(item)"
      >
        <!-- Expand/collapse chevron for objects/arrays -->
        <ChevronRightIcon
          v-if="item.hasChildren"
          class="size-3 shrink-0 text-gray-400 transition-transform"
          :class="{ 'rotate-90': expanded.has(item.path) }"
        />
        <span v-else class="inline-block size-3" />

        <!-- Type icon -->
        <span class="shrink-0 text-[10px]" :class="typeColor(item.type)">
          {{ typeIcon(item.type) }}
        </span>

        <!-- Field name -->
        <span class="truncate font-medium text-gray-700 dark:text-gray-300">{{ item.name }}</span>

        <!-- Type badge -->
        <span class="ml-auto shrink-0 text-[10px] text-gray-400">{{ item.type }}</span>

        <!-- Value preview for primitives -->
        <span
          v-if="item.preview !== undefined"
          class="ml-1 max-w-24 shrink-0 truncate text-[10px] text-gray-400 dark:text-gray-500"
        >{{ item.preview }}</span>
      </div>

      <!-- Children (recursive via v-if to save rendering) -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ChevronRightIcon } from '@heroicons/vue/20/solid'

export interface TreeNode {
  name: string
  path: string
  type: string
  hasChildren: boolean
  depth: number
  preview?: string
  children?: TreeNode[]
}

const props = defineProps<{
  json: any
  parentPath?: string
}>()

const emit = defineEmits<{
  'drag-field': [path: string, type: string]
}>()

const expanded = ref(new Set<string>())
const isDragging = ref('')

function parseJson(data: any, parentPath: string, depth: number): TreeNode[] {
  if (data == null) return []
  const nodes: TreeNode[] = []

  if (Array.isArray(data)) {
    if (data.length > 0) {
      const sample = data[0]
      if (typeof sample === 'object' && sample !== null) {
        const arrNode: TreeNode = {
          name: '[*]',
          path: parentPath ? `${parentPath}.[*]` : '[*]',
          type: 'array',
          hasChildren: true,
          depth,
          children: parseJson(sample, parentPath ? `${parentPath}.[*]` : '[*]', depth + 1),
        }
        nodes.push(arrNode)
      } else {
        nodes.push({
          name: '[*]',
          path: parentPath ? `${parentPath}.[*]` : '[*]',
          type: `${typeof sample}[]`,
          hasChildren: false,
          depth,
          preview: `[${data.length} items]`,
        })
      }
    }
    return nodes
  }

  if (typeof data === 'object') {
    for (const [key, value] of Object.entries(data)) {
      const path = parentPath ? `${parentPath}.${key}` : key
      if (value === null) {
        nodes.push({ name: key, path, type: 'null', hasChildren: false, depth, preview: 'null' })
      } else if (Array.isArray(value)) {
        const childNodes = parseJson(value, path, depth + 1)
        nodes.push({
          name: key,
          path,
          type: 'array',
          hasChildren: childNodes.length > 0,
          depth,
          preview: `[${value.length}]`,
          children: childNodes,
        })
      } else if (typeof value === 'object') {
        const childNodes = parseJson(value, path, depth + 1)
        nodes.push({
          name: key,
          path,
          type: 'object',
          hasChildren: childNodes.length > 0,
          depth,
          children: childNodes,
        })
      } else {
        const t = typeof value as string
        nodes.push({
          name: key,
          path,
          type: t,
          hasChildren: false,
          depth,
          preview: String(value).slice(0, 30),
        })
      }
    }
  }

  return nodes
}

function flattenVisible(nodes: TreeNode[]): TreeNode[] {
  const result: TreeNode[] = []
  for (const n of nodes) {
    result.push(n)
    if (n.hasChildren && expanded.value.has(n.path) && n.children) {
      result.push(...flattenVisible(n.children))
    }
  }
  return result
}

const rootNodes = computed(() => parseJson(props.json, props.parentPath ?? '', 0))
const treeNodes = computed(() => flattenVisible(rootNodes.value))

watch(rootNodes, () => {
  // auto expand first level
  for (const n of rootNodes.value) {
    if (n.hasChildren) expanded.value.add(n.path)
  }
}, { immediate: true })

function toggle(item: TreeNode) {
  if (!item.hasChildren) return
  if (expanded.value.has(item.path)) {
    expanded.value.delete(item.path)
  } else {
    expanded.value.add(item.path)
  }
}

function onDragStart(event: DragEvent, item: TreeNode) {
  isDragging.value = item.path
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'copy'
    event.dataTransfer.setData('application/json-field', JSON.stringify({ path: item.path, type: item.type }))
  }
  emit('drag-field', item.path, item.type)
}

function typeIcon(type: string): string {
  const map: Record<string, string> = {
    string: 'Aa',
    number: '#',
    boolean: '⊘',
    object: '{}',
    array: '[]',
    null: '∅',
  }
  return map[type] || type.charAt(0).toUpperCase()
}

function typeColor(type: string): string {
  const map: Record<string, string> = {
    string: 'text-green-500',
    number: 'text-blue-500',
    boolean: 'text-orange-500',
    object: 'text-purple-500',
    array: 'text-sky-500',
    null: 'text-gray-400',
  }
  return map[type] || 'text-gray-500'
}
</script>
