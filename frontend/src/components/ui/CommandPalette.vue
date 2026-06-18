<template>
  <TransitionRoot :show="open" as="template" @after-leave="query = ''">
    <Dialog class="relative z-[60]" @close="open = false">
      <TransitionChild as="template" enter="ease-out duration-200" enter-from="opacity-0" enter-to="" leave="ease-in duration-150" leave-from="" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-900/50 transition-opacity" />
      </TransitionChild>
      <div class="fixed inset-0 z-[60] w-screen overflow-y-auto p-4 sm:p-6 md:p-20">
        <TransitionChild as="template" enter="ease-out duration-200" enter-from="opacity-0 scale-95" enter-to="scale-100" leave="ease-in duration-150" leave-from="scale-100" leave-to="opacity-0 scale-95">
          <DialogPanel class="mx-auto max-w-xl transform divide-y divide-gray-100 overflow-hidden rounded-xl bg-white shadow-2xl ring-1 ring-black/5 transition-all dark:divide-white/10 dark:bg-gray-800 dark:ring-white/10">
            <div class="relative">
              <MagnifyingGlassIcon class="pointer-events-none absolute top-3.5 left-4 size-5 text-gray-400" aria-hidden="true" />
              <input
                ref="inputRef"
                v-model="query"
                class="h-12 w-full border-0 bg-transparent pl-11 pr-4 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm dark:text-white"
                :placeholder="t('search.placeholder')"
                @keydown.escape="open = false"
              />
            </div>
            <ul v-if="filteredItems.length > 0" class="max-h-80 scroll-py-2 overflow-y-auto py-2">
              <li
                v-for="item in filteredItems"
                :key="item.id"
                class="flex cursor-pointer select-none items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-sky-600 hover:text-white dark:text-gray-300 dark:hover:bg-sky-500"
                @click="execute(item)"
              >
                <component :is="item.icon" class="size-5 shrink-0 opacity-60" aria-hidden="true" />
                <div class="min-w-0 flex-1">
                  <p class="truncate font-medium">{{ item.label }}</p>
                  <p class="truncate text-xs opacity-60">{{ item.description }}</p>
                </div>
                <span v-if="item.shortcut" class="ml-auto shrink-0 text-xs font-medium opacity-40">{{ item.shortcut }}</span>
              </li>
            </ul>
            <div v-else-if="query" class="px-6 py-14 text-center text-sm text-gray-500 dark:text-gray-400">
              {{ t('search.noResults') }}
            </div>
          </DialogPanel>
        </TransitionChild>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch, onMounted, onUnmounted, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Dialog, DialogPanel, TransitionChild, TransitionRoot } from '@headlessui/vue'
import {
  MagnifyingGlassIcon,
  HomeIcon,
  RectangleGroupIcon,
  FolderIcon,
  ClipboardDocumentListIcon,
  Cog6ToothIcon,
  PlusIcon,
  ArrowUpTrayIcon,
  SunIcon,
  MoonIcon,
  LanguageIcon,
} from '@heroicons/vue/24/outline'

interface SearchItem {
  id: string
  label: string
  description: string
  icon: Component
  action: () => void
  shortcut?: string
  keywords?: string
}

const { t, locale } = useI18n()
const router = useRouter()

const open = ref(false)
const query = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

defineExpose({ open })

watch(open, (v) => {
  if (v) nextTick(() => inputRef.value?.focus())
})

function onKeyDown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    open.value = !open.value
  }
}

onMounted(() => window.addEventListener('keydown', onKeyDown))
onUnmounted(() => window.removeEventListener('keydown', onKeyDown))

function toggleTheme() {
  const html = document.documentElement
  const isDark = html.classList.contains('dark')
  if (isDark) {
    html.classList.remove('dark')
    localStorage.setItem('df_theme', 'light')
  } else {
    html.classList.add('dark')
    localStorage.setItem('df_theme', 'dark')
  }
}

function toggleLocale() {
  const next = locale.value === 'zh-CN' ? 'en' : 'zh-CN'
  locale.value = next
  localStorage.setItem('df_locale', next)
}

const allItems = computed<SearchItem[]>(() => [
  { id: 'nav-dashboard', label: t('nav.dashboard'), description: t('search.goTo', { page: t('nav.dashboard') }), icon: HomeIcon, action: () => router.push('/dashboard'), keywords: 'dashboard 仪表盘 home 首页' },
  { id: 'nav-pipeline', label: t('nav.pipeline'), description: t('search.goTo', { page: t('nav.pipeline') }), icon: RectangleGroupIcon, action: () => router.push('/pipelines'), keywords: 'pipeline 流水线 pipelines' },
  { id: 'nav-files', label: t('nav.files'), description: t('search.goTo', { page: t('nav.files') }), icon: FolderIcon, action: () => router.push('/files'), keywords: 'files 文件 file manager' },
  { id: 'nav-tasks', label: t('nav.tasks'), description: t('search.goTo', { page: t('nav.tasks') }), icon: ClipboardDocumentListIcon, action: () => router.push('/tasks'), keywords: 'tasks 任务 task monitor' },
  { id: 'nav-settings', label: t('nav.settings'), description: t('search.goTo', { page: t('nav.settings') }), icon: Cog6ToothIcon, action: () => router.push('/settings'), keywords: 'settings 设置 config preference' },
  { id: 'action-new-pipeline', label: t('search.newPipeline'), description: t('search.createNewPipeline'), icon: PlusIcon, action: () => router.push('/pipelines'), keywords: 'new create 新建 创建' },
  { id: 'action-upload', label: t('search.uploadFiles'), description: t('search.uploadDesc'), icon: ArrowUpTrayIcon, action: () => router.push('/files'), keywords: 'upload 上传' },
  { id: 'action-theme', label: t('search.toggleTheme'), description: t('search.toggleThemeDesc'), icon: SunIcon, action: toggleTheme, keywords: 'theme dark light 主题 深色 浅色 暗色' },
  { id: 'action-locale', label: t('search.toggleLang'), description: t('search.toggleLangDesc'), icon: LanguageIcon, action: toggleLocale, keywords: 'language 语言 中文 english i18n' },
])

const filteredItems = computed(() => {
  if (!query.value) return allItems.value
  const q = query.value.toLowerCase()
  return allItems.value.filter(item =>
    item.label.toLowerCase().includes(q)
    || item.description.toLowerCase().includes(q)
    || (item.keywords?.toLowerCase().includes(q))
  )
})

function execute(item: SearchItem) {
  open.value = false
  item.action()
}
</script>
