<template>
  <TransitionRoot as="template" :show="open">
    <div class="absolute inset-y-0 right-0 z-30 flex">
      <TransitionChild as="template" enter="transform transition ease-in-out duration-300" enter-from="translate-x-full" enter-to="translate-x-0" leave="transform transition ease-in-out duration-300" leave-from="translate-x-0" leave-to="translate-x-full">
        <div class="relative w-72 border-l border-gray-200 bg-white shadow-xl dark:border-white/10 dark:bg-gray-800">
          <div class="flex h-full flex-col overflow-y-auto">
            <div class="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-white/10">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white">{{ t('editor.nodeLibrary') }}</h3>
              <button type="button" class="rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-white" @click="$emit('close')">
                <XMarkIcon class="size-5" />
              </button>
            </div>

            <div class="border-b border-gray-200 px-3 py-3 dark:border-white/10">
              <input
                v-model="search"
                type="text"
                placeholder="Search nodes..."
                class="w-full rounded-md bg-white px-3 py-2 text-sm outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-sky-600 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-sky-500"
              />
            </div>

            <div class="flex-1 overflow-y-auto">
              <Disclosure v-for="(items, category) in groupedNodes" :key="category" v-slot="{ open: isOpen }" default-open>
                <DisclosureButton class="flex w-full items-center justify-between px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                  {{ t(`nodeCategories.${category}`, category) }}
                  <ChevronRightIcon :class="[isOpen ? 'rotate-90' : '', 'size-4 transition-transform']" />
                </DisclosureButton>
                <DisclosurePanel class="px-3 pb-3">
                  <div class="space-y-1">
                    <div
                      v-for="item in items"
                      :key="item.type"
                      class="flex cursor-grab items-center gap-2 rounded-lg border border-transparent px-2 py-2 text-sm text-gray-700 transition-colors hover:border-sky-200 hover:bg-sky-50 hover:text-sky-700 active:cursor-grabbing dark:text-gray-300 dark:hover:border-sky-500/30 dark:hover:bg-sky-500/10 dark:hover:text-sky-400"
                      draggable="true"
                      @dragstart="$emit('drag-start', item.type)"
                    >
                      <component :is="heroIcon(item.icon)" class="size-4" />
                      <span>{{ item.label }}</span>
                    </div>
                  </div>
                </DisclosurePanel>
              </Disclosure>
            </div>
          </div>
        </div>
      </TransitionChild>
    </div>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Disclosure, DisclosureButton, DisclosurePanel, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { ChevronRightIcon } from '@heroicons/vue/20/solid'
import * as HeroIcons from '@heroicons/vue/24/outline'
import { useNodeSchemaStore } from '@/stores/nodeSchema'

defineProps<{ open: boolean }>()
defineEmits<{ 'drag-start': [type: string]; close: [] }>()

const nodeSchemaStore = useNodeSchemaStore()
const { t } = useI18n()
const search = ref('')

const categoryLabels: Record<string, string> = {}

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
