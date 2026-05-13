<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useNodeSchemaStore } from '@/stores/nodeSchema'

const nodeSchemaStore = useNodeSchemaStore()

onMounted(() => {
  nodeSchemaStore.fetch()

  const theme = localStorage.getItem('df_theme') || 'system'
  const html = document.documentElement
  if (theme === 'dark') {
    html.classList.add('dark')
  } else if (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    html.classList.add('dark')
  }
})
</script>
