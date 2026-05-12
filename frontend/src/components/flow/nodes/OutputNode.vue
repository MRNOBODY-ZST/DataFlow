<template>
  <div class="bg-white border-2 border-green-500 rounded-xl px-4 py-3 min-w-36 shadow-sm">
    <div class="flex items-center gap-2 mb-1">
      <span class="text-base">💾</span>
      <span class="text-xs font-semibold text-green-700">MinIO 写出</span>
    </div>
    <p class="text-xs text-gray-500 truncate max-w-32">{{ props.data?.key || '未配置' }}</p>
    <Handle type="target" :position="Position.Left" />
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
const props = defineProps<{ data: Record<string, any> }>()
</script>
