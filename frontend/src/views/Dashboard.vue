<template>
  <AppNav title="我的流水线" description="创建、管理并进入可视化编排画布。">
    <template #actions>
      <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="openCreate">
        新建流水线
      </button>
    </template>

    <div class="space-y-6">
      <div class="grid gap-4 md:grid-cols-3">
        <div class="rounded-lg bg-white p-5 shadow-sm ring-1 ring-gray-200">
          <dt class="text-sm font-medium text-gray-500">流水线总数</dt>
          <dd class="mt-2 text-3xl font-semibold tracking-tight text-gray-900">{{ pipelineStore.pipelines.length }}</dd>
        </div>
        <div class="rounded-lg bg-white p-5 shadow-sm ring-1 ring-gray-200">
          <dt class="text-sm font-medium text-gray-500">最近更新</dt>
          <dd class="mt-2 text-sm font-semibold tracking-tight text-gray-900">{{ latestUpdated }}</dd>
        </div>
        <div class="rounded-lg bg-white p-5 shadow-sm ring-1 ring-gray-200">
          <dt class="text-sm font-medium text-gray-500">当前用户</dt>
          <dd class="mt-2 text-3xl font-semibold tracking-tight text-gray-900">{{ auth.username || '—' }}</dd>
        </div>
      </div>

      <div class="overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-gray-200">
        <div v-if="pipelineStore.loading" class="px-6 py-16 text-center text-sm text-gray-500">加载中...</div>
        <div v-else-if="pipelineStore.pipelines.length === 0" class="px-6 py-16 text-center">
          <div class="mx-auto max-w-sm rounded-lg border border-dashed border-gray-300 px-6 py-10">
            <FolderPlusIcon class="mx-auto size-10 text-gray-400" />
            <h3 class="mt-2 text-sm font-semibold text-gray-900">还没有流水线</h3>
            <p class="mt-1 text-sm text-gray-500">先创建一个流水线，然后进入编辑器拖拽节点。</p>
            <div class="mt-6">
              <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="openCreate">新建流水线</button>
            </div>
          </div>
        </div>
        <ul v-else role="list" class="divide-y divide-gray-200">
          <li v-for="pipeline in pipelineStore.pipelines" :key="pipeline.id" class="flex flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-gray-900">{{ pipeline.name }}</p>
              <p class="mt-1 truncate text-sm text-gray-500">{{ pipeline.description || '无描述' }}</p>
              <div class="mt-2 flex items-center gap-3 text-xs text-gray-500">
                <span>#{{ pipeline.id }}</span>
                <span>{{ new Date(pipeline.updatedAt).toLocaleString() }}</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500" @click="router.push(`/editor/${pipeline.id}`)">编辑</button>
              <button type="button" class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-red-600 shadow-xs inset-ring inset-ring-red-200 hover:bg-red-50" @click="deletePipeline(pipeline.id)">删除</button>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </AppNav>

  <TransitionRoot as="template" :show="showCreate">
    <Dialog class="relative z-20" @close="showCreate = false">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity"></div>
      </TransitionChild>
      <div class="fixed inset-0 z-20 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
              <form @submit.prevent="createPipeline">
                <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                  <DialogTitle as="h3" class="text-base font-semibold text-gray-900">新建流水线</DialogTitle>
                  <div class="mt-4 space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-900">名称</label>
                      <input v-model="newName" required class="mt-2 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6" />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-900">描述</label>
                      <input v-model="newDesc" class="mt-2 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6" />
                    </div>
                  </div>
                </div>
                <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                  <button type="submit" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 sm:ml-3 sm:w-auto">创建</button>
                  <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto" @click="showCreate = false">取消</button>
                </div>
              </form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { FolderPlusIcon } from '@heroicons/vue/24/outline'
import AppNav from '@/components/ui/AppNav.vue'
import { useAuthStore } from '@/stores/auth'
import { usePipelineStore } from '@/stores/pipeline'

const router = useRouter()
const auth = useAuthStore()
const pipelineStore = usePipelineStore()

const showCreate = ref(false)
const newName = ref('')
const newDesc = ref('')

const latestUpdated = computed(() => {
  const first = pipelineStore.pipelines[0]
  return first ? new Date(first.updatedAt).toLocaleString() : '暂无数据'
})

onMounted(() => pipelineStore.fetchAll())

function openCreate() {
  newName.value = ''
  newDesc.value = ''
  showCreate.value = true
}

async function createPipeline() {
  const pipeline = await pipelineStore.createPipeline(newName.value, newDesc.value)
  showCreate.value = false
  router.push(`/editor/${pipeline.id}`)
}

async function deletePipeline(id: number) {
  if (!confirm('确认删除该流水线？')) return
  await pipelineStore.deletePipeline(id)
}
</script>
