<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar -->
    <nav class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <span class="text-lg font-bold text-indigo-600">DataFlow</span>
      <div class="flex items-center gap-4">
        <router-link to="/tasks" class="text-sm text-gray-600 hover:text-indigo-600">任务监控</router-link>
        <span class="text-sm text-gray-500">{{ auth.username }}</span>
        <button class="text-sm text-red-500 hover:text-red-700" @click="logout">退出</button>
      </div>
    </nav>

    <main class="max-w-5xl mx-auto px-6 py-8">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-gray-800">我的流水线</h2>
        <button
          class="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          @click="openCreate"
        >
          + 新建流水线
        </button>
      </div>

      <div v-if="pipelineStore.loading" class="text-center text-gray-400 py-16">加载中...</div>
      <div v-else-if="pipelineStore.pipelines.length === 0" class="text-center text-gray-400 py-16">
        暂无流水线，点击「新建」开始
      </div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="p in pipelineStore.pipelines"
          :key="p.id"
          class="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow cursor-pointer"
          @click="router.push(`/editor/${p.id}`)"
        >
          <h3 class="font-semibold text-gray-800 truncate">{{ p.name }}</h3>
          <p class="text-xs text-gray-500 mt-1 truncate">{{ p.description || '无描述' }}</p>
          <p class="text-xs text-gray-400 mt-3">{{ new Date(p.updatedAt).toLocaleString() }}</p>
          <div class="flex gap-2 mt-4">
            <button
              class="text-xs text-indigo-600 hover:underline"
              @click.stop="router.push(`/editor/${p.id}`)"
            >
              编辑
            </button>
            <button
              class="text-xs text-red-500 hover:underline"
              @click.stop="deletePipeline(p.id)"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Create modal -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
        <h3 class="text-lg font-semibold mb-4">新建流水线</h3>
        <form class="space-y-3" @submit.prevent="createPipeline">
          <input
            v-model="newName"
            placeholder="流水线名称"
            required
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            v-model="newDesc"
            placeholder="描述（可选）"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" class="text-sm text-gray-500" @click="showCreate = false">取消</button>
            <button
              type="submit"
              class="bg-indigo-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-indigo-500"
            >
              创建
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePipelineStore } from '@/stores/pipeline'

const router = useRouter()
const auth = useAuthStore()
const pipelineStore = usePipelineStore()

const showCreate = ref(false)
const newName = ref('')
const newDesc = ref('')

onMounted(() => pipelineStore.fetchAll())

function openCreate() {
  newName.value = ''
  newDesc.value = ''
  showCreate.value = true
}

async function createPipeline() {
  const p = await pipelineStore.createPipeline(newName.value, newDesc.value)
  showCreate.value = false
  router.push(`/editor/${p.id}`)
}

async function deletePipeline(id: number) {
  if (!confirm('确认删除？')) return
  await pipelineStore.deletePipeline(id)
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
