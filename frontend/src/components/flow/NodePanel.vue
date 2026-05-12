<template>
  <div class="w-48 bg-white border-r border-gray-200 flex flex-col p-3 gap-1 shrink-0 overflow-y-auto">
    <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">节点</p>

    <div
      v-for="item in nodeList"
      :key="item.type"
      class="flex items-center gap-2 px-2 py-2 rounded-lg text-sm text-gray-700 cursor-grab hover:bg-indigo-50 hover:text-indigo-700 active:cursor-grabbing transition-colors border border-transparent hover:border-indigo-200"
      draggable="true"
      @dragstart="$emit('drag-start', item.type)"
    >
      <span class="text-base">{{ item.icon }}</span>
      <span>{{ item.label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{ 'drag-start': [type: string] }>()

const nodeList = [
  { type: 'csv_reader',   icon: '📄', label: 'CSV 读取' },
  { type: 'json_reader',  icon: '📋', label: 'JSON 读取' },
  { type: 'minio_reader', icon: '☁️',  label: 'MinIO 读取' },
  { type: 'filter',       icon: '🔍', label: '过滤' },
  { type: 'map',          icon: '🔄', label: '字段映射' },
  { type: 'aggregate',    icon: '📊', label: '聚合' },
  { type: 'image_resize', icon: '🖼️', label: '图片缩放' },
  { type: 'image_ocr',    icon: '🔡', label: '图片 OCR' },
  { type: 'video_extract',icon: '🎬', label: '视频抽帧' },
  { type: 'minio_writer', icon: '💾', label: 'MinIO 写出' },
]
</script>
