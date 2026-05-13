<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useNodeSchemaStore } from '@/stores/nodeSchema'

const nodeSchemaStore = useNodeSchemaStore()

onMounted(() => {
  nodeSchemaStore.fetch()
})
</script>
