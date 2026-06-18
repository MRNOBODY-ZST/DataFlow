<template>
  <div class="bg-white border-2 border-gray-300 rounded-xl px-4 py-3 min-w-36 shadow-sm">
    <div class="flex items-center gap-2 mb-1">
      <span class="text-xs font-semibold text-gray-600 font-mono">{{ props.type }}</span>
    </div>
    <p class="text-xs text-gray-400">{{ props.data?.label || '' }}</p>
    <Handle type="target" :position="Position.Left" />
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
const props = defineProps<{ type: string; data: Record<string, any> }>()
</script>
