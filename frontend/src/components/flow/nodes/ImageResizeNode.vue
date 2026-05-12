<template>
  <div class="bg-white border-2 border-purple-400 rounded-xl px-4 py-3 min-w-36 shadow-sm">
    <div class="flex items-center gap-2 mb-1">
      <span class="text-base">🖼️</span>
      <span class="text-xs font-semibold text-purple-700">图片缩放</span>
    </div>
    <p class="text-xs text-gray-500">
      {{ props.data?.width ? `${props.data.width}w` : '' }}
      {{ props.data?.height ? `× ${props.data.height}h` : '' }}
      {{ (!props.data?.width && !props.data?.height) ? '未配置' : '' }}
    </p>
    <Handle type="target" :position="Position.Left" />
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
const props = defineProps<{ data: Record<string, any> }>()
</script>
