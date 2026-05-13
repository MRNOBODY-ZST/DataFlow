<template>
  <div class="w-56 shrink-0 overflow-y-auto border-r border-gray-200 bg-white">
    <div class="border-b border-gray-100 px-3 py-3">
      <input
        v-model="search"
        type="text"
        placeholder="搜索节点..."
        class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
      />
    </div>

    <div v-for="(items, category) in groupedNodes" :key="category" class="px-3 py-3">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">
        {{ categoryLabels[category] || category }}
      </p>
      <div class="space-y-1">
        <div
          v-for="item in items"
          :key="item.type"
          class="flex cursor-grab items-center gap-2 rounded-lg border border-transparent px-2 py-2 text-sm text-gray-700 transition-colors hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700 active:cursor-grabbing"
          draggable="true"
          @dragstart="$emit('drag-start', item.type)"
        >
          <component :is="heroIcon(item.icon)" class="size-4" />
          <span>{{ item.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import * as HeroIcons from '@heroicons/vue/24/outline'
import { useNodeSchemaStore } from '@/stores/nodeSchema'

const emit = defineEmits<{ 'drag-start': [type: string] }>()
defineExpose({ emit })

const nodeSchemaStore = useNodeSchemaStore()
const search = ref('')

const categoryLabels: Record<string, string> = {
  readers: '读取',
  transforms: '转换',
  media: '媒体处理',
  writers: '输出',
}

const groupedNodes = computed(() => {
  const query = search.value.trim().toLowerCase()
  const result: Record<string, typeof nodeSchemaStore.schemas> = {}
  for (const [category, items] of Object.entries(nodeSchemaStore.byCategory)) {
    const filtered = items.filter((item) => {
      if (!query) return true
      return item.label.toLowerCase().includes(query) || item.type.toLowerCase().includes(query)
    })
    if (filtered.length) result[category] = filtered
  }
  return result
})

function heroIcon(name: string) {
  const icons = HeroIcons as Record<string, any>
  return icons[name] ?? HeroIcons.Square3Stack3DIcon
}
</script>
