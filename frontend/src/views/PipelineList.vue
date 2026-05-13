<template>
  <AppLayout :title="t('pipeline.title')">
    <div class="py-6 px-4 sm:px-6 lg:px-8">
      <div class="sm:flex sm:items-center sm:justify-between">
        <div>
          <h2 class="text-base font-semibold text-gray-900 dark:text-white">{{ t('pipeline.allPipelines') }}</h2>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('pipeline.description') }}</p>
        </div>
        <button type="button" class="mt-4 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 sm:mt-0 dark:bg-indigo-500 dark:shadow-none dark:hover:bg-indigo-400" @click="openCreate">
          <span class="flex items-center gap-1.5">
            <PlusIcon class="size-4" />
            {{ t('pipeline.newPipeline') }}
          </span>
        </button>
      </div>

      <div class="mt-6 overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-gray-200 dark:bg-gray-800/75 dark:ring-white/10">
        <div v-if="pipelineStore.loading" class="px-6 py-16 text-center text-sm text-gray-500 dark:text-gray-400">{{ t('common.loading') }}</div>
        <div v-else-if="pipelineStore.pipelines.length === 0" class="px-6 py-16 text-center">
          <div class="mx-auto max-w-sm rounded-lg border border-dashed border-gray-300 px-6 py-10 dark:border-white/20">
            <FolderPlusIcon class="mx-auto size-10 text-gray-400" />
            <h3 class="mt-2 text-sm font-semibold text-gray-900 dark:text-white">{{ t('pipeline.noPipelines') }}</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('pipeline.createFirst') }}</p>
            <div class="mt-6">
              <button type="button" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-400" @click="openCreate">{{ t('pipeline.newPipeline') }}</button>
            </div>
          </div>
        </div>
        <ul v-else role="list" class="divide-y divide-gray-100 dark:divide-white/5">
          <li v-for="pipeline in pipelineStore.pipelines" :key="pipeline.id" class="flex items-center justify-between gap-x-6 px-4 py-5 sm:px-6">
            <div class="min-w-0">
              <div class="flex items-start gap-x-3">
                <p class="text-sm/6 font-semibold text-gray-900 dark:text-white">{{ pipeline.name }}</p>
                <p class="mt-0.5 rounded-md px-1.5 py-0.5 text-xs font-medium text-gray-400 bg-gray-100 inset-ring inset-ring-gray-500/10 dark:bg-gray-400/10 dark:text-gray-500 dark:inset-ring-gray-400/20">ID: {{ pipeline.id }}</p>
                <p class="mt-0.5 rounded-md px-1.5 py-0.5 text-xs font-medium" :class="pipelineStatusClass(pipeline)">{{ pipelineStatusLabel(pipeline) }}</p>
              </div>
              <div class="mt-1 flex items-center gap-x-2 text-xs/5 text-gray-500 dark:text-gray-400">
                <p class="whitespace-nowrap">{{ pipeline.description || t('pipeline.noDescription') }}</p>
                <svg viewBox="0 0 2 2" class="size-0.5 fill-current"><circle cx="1" cy="1" r="1" /></svg>
                <p class="whitespace-nowrap">{{ t('pipeline.nodes', { n: nodeCount(pipeline) }) }}</p>
                <svg viewBox="0 0 2 2" class="size-0.5 fill-current"><circle cx="1" cy="1" r="1" /></svg>
                <p class="whitespace-nowrap">{{ t('pipeline.updated') }} <time>{{ new Date(pipeline.updatedAt).toLocaleDateString() }}</time></p>
              </div>
            </div>
            <div class="flex flex-none items-center gap-x-4">
              <button type="button" class="hidden rounded-md bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 sm:block dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20" @click="router.push(`/editor/${pipeline.id}`)">
                {{ t('common.edit') }}<span class="sr-only">, {{ pipeline.name }}</span>
              </button>
              <Menu as="div" class="relative flex-none">
                <MenuButton class="relative block text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
                  <span class="absolute -inset-2.5"></span>
                  <span class="sr-only">{{ t('pipeline.openOptions') }}</span>
                  <EllipsisVerticalIcon class="size-5" aria-hidden="true" />
                </MenuButton>
                <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="transform scale-100" leave-to-class="transform opacity-0 scale-95">
                  <MenuItems class="absolute right-0 z-10 mt-2 w-32 origin-top-right rounded-md bg-white py-2 shadow-lg outline-1 outline-gray-900/5 dark:bg-gray-800 dark:shadow-none dark:-outline-offset-1 dark:outline-white/10">
                    <MenuItem v-slot="{ active }">
                      <button type="button" :class="[active ? 'bg-gray-50 outline-hidden dark:bg-white/5' : '', 'block w-full px-3 py-1 text-left text-sm/6 text-gray-900 dark:text-white']" @click="router.push(`/editor/${pipeline.id}`)">
                        {{ t('common.edit') }}<span class="sr-only">, {{ pipeline.name }}</span>
                      </button>
                    </MenuItem>
                    <MenuItem v-slot="{ active }">
                      <button type="button" :class="[active ? 'bg-gray-50 outline-hidden dark:bg-white/5' : '', 'block w-full px-3 py-1 text-left text-sm/6 text-gray-900 dark:text-white']" @click="duplicatePipeline(pipeline)">
                        {{ t('pipeline.duplicate') }}<span class="sr-only">, {{ pipeline.name }}</span>
                      </button>
                    </MenuItem>
                    <MenuItem v-slot="{ active }">
                      <button type="button" :class="[active ? 'bg-gray-50 outline-hidden dark:bg-white/5' : '', 'block w-full px-3 py-1 text-left text-sm/6 text-red-600 dark:text-red-400']" @click="deletePipeline(pipeline.id)">
                        {{ t('common.delete') }}<span class="sr-only">, {{ pipeline.name }}</span>
                      </button>
                    </MenuItem>
                  </MenuItems>
                </transition>
              </Menu>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </AppLayout>

  <!-- Create Pipeline Dialog -->
  <TransitionRoot as="template" :show="showCreate">
    <Dialog class="relative z-50" @close="showCreate = false">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="" leave="ease-in duration-200" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/75 transition-opacity dark:bg-gray-900/50"></div>
      </TransitionChild>
      <div class="fixed inset-0 z-50 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to=" translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from=" translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg dark:bg-gray-800 dark:outline dark:-outline-offset-1 dark:outline-white/10">
              <form @submit.prevent="createPipeline">
                <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                  <DialogTitle as="h3" class="text-base font-semibold text-gray-900 dark:text-white">{{ t('pipeline.newPipeline') }}</DialogTitle>
                  <div class="mt-4 space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('pipeline.name') }}</label>
                      <input v-model="newName" required class="mt-2 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:focus:outline-indigo-500" />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('pipeline.descLabel') }}</label>
                      <input v-model="newDesc" class="mt-2 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:focus:outline-indigo-500" />
                    </div>
                  </div>
                </div>
                <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 dark:bg-gray-800/50">
                  <button type="submit" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 sm:ml-3 sm:w-auto dark:bg-indigo-500 dark:hover:bg-indigo-400">{{ t('common.create') }}</button>
                  <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto dark:bg-white/10 dark:text-white dark:inset-ring-white/5 dark:hover:bg-white/20" @click="showCreate = false">{{ t('common.cancel') }}</button>
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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Dialog, DialogPanel, DialogTitle, Menu, MenuButton, MenuItem, MenuItems, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { FolderPlusIcon, PlusIcon } from '@heroicons/vue/24/outline'
import { EllipsisVerticalIcon } from '@heroicons/vue/20/solid'
import AppLayout from '@/components/layout/AppLayout.vue'
import { usePipelineStore } from '@/stores/pipeline'

const { t } = useI18n()
const router = useRouter()
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
  const pipeline = await pipelineStore.createPipeline(newName.value, newDesc.value)
  showCreate.value = false
  router.push(`/editor/${pipeline.id}`)
}

async function duplicatePipeline(pipeline: any) {
  await pipelineStore.createPipeline(`${pipeline.name} (copy)`, pipeline.description || '')
}

async function deletePipeline(id: number) {
  if (!confirm(t('pipeline.confirmDelete'))) return
  await pipelineStore.deletePipeline(id)
}

function nodeCount(pipeline: any): number {
  return pipeline.nodes?.length ?? 0
}

function pipelineStatusLabel(pipeline: any): string {
  const count = nodeCount(pipeline)
  if (count === 0) return t('pipeline.draft')
  return t('pipeline.nodes', { n: count })
}

function pipelineStatusClass(pipeline: any): string {
  const count = nodeCount(pipeline)
  if (count === 0) return 'bg-gray-50 text-gray-600 inset-ring inset-ring-gray-500/10 dark:bg-gray-400/10 dark:text-gray-400 dark:inset-ring-gray-400/20'
  return 'bg-green-50 text-green-700 inset-ring inset-ring-green-600/20 dark:bg-green-400/10 dark:text-green-400 dark:inset-ring-green-500/20'
}
</script>
