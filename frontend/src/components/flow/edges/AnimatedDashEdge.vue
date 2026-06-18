<template>
  <BaseEdge :path="path" :style="edgeStyle" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { BaseEdge, getBezierPath } from '@vue-flow/core'

const props = defineProps<{
  id: string
  sourceX: number
  sourceY: number
  targetX: number
  targetY: number
  sourcePosition: any
  targetPosition: any
  markerEnd?: string
  style?: Record<string, any>
}>()

const path = computed(() => {
  const [p] = getBezierPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    targetX: props.targetX,
    targetY: props.targetY,
    sourcePosition: props.sourcePosition,
    targetPosition: props.targetPosition,
  })
  return p
})

const edgeStyle = {
  stroke: '#94a3b8',
  strokeWidth: 2,
  strokeDasharray: '6 4',
  animation: 'dash-flow 0.5s linear infinite',
}
</script>
