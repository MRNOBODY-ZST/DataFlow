<template>
  <!-- Bell button with popover -->
  <Popover as="div" class="relative inline-flex">
    <PopoverButton class="-m-2.5 p-2 text-gray-400 hover:text-gray-500 dark:hover:text-white">
      <span class="sr-only">{{ t('notification.title') }}</span>
      <BellIcon class="size-5" aria-hidden="true" />
      <span
        v-if="store.unreadCount > 0"
        class="absolute top-1 right-1 flex size-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white"
      >{{ store.unreadCount > 9 ? '9+' : store.unreadCount }}</span>
    </PopoverButton>
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1"
    >
      <PopoverPanel class="absolute right-0 z-50 mt-3 w-80 origin-top-right rounded-xl bg-white shadow-lg ring-1 ring-black/5 dark:bg-gray-800 dark:ring-white/10">
        <div class="flex items-center justify-between border-b border-gray-100 px-4 py-3 dark:border-white/10">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white">{{ t('notification.title') }}</h3>
          <button
            v-if="store.items.length > 0"
            type="button"
            class="text-xs text-sky-600 hover:text-sky-500 dark:text-sky-400"
            @click="store.markAllRead()"
          >{{ t('notification.markAllRead') }}</button>
        </div>
        <div class="max-h-80 overflow-y-auto">
          <div v-if="store.items.length === 0" class="px-4 py-10 text-center text-sm text-gray-400 dark:text-gray-500">
            {{ t('notification.empty') }}
          </div>
          <div
            v-for="n in store.items"
            :key="n.id"
            class="flex gap-3 border-b border-gray-50 px-4 py-3 last:border-0 dark:border-white/5"
            :class="n.read ? 'opacity-60' : ''"
            @click="store.markRead(n.id)"
          >
            <div class="mt-0.5 shrink-0">
              <CheckCircleIcon v-if="n.type === 'success'" class="size-5 text-green-500" />
              <XCircleIcon v-else-if="n.type === 'error'" class="size-5 text-red-500" />
              <InformationCircleIcon v-else class="size-5 text-sky-500" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-gray-900 dark:text-white">{{ n.title }}</p>
              <p class="mt-0.5 truncate text-xs text-gray-500 dark:text-gray-400">{{ n.message }}</p>
              <p class="mt-1 text-[10px] text-gray-400 dark:text-gray-500">{{ timeAgo(n.time) }}</p>
            </div>
            <button type="button" class="mt-0.5 shrink-0 text-gray-300 hover:text-gray-500 dark:text-gray-600 dark:hover:text-gray-400" @click.stop="store.remove(n.id)">
              <XMarkIcon class="size-4" />
            </button>
          </div>
        </div>
        <div v-if="store.items.length > 0" class="border-t border-gray-100 px-4 py-2 dark:border-white/10">
          <button type="button" class="w-full text-center text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" @click="store.clearAll()">{{ t('notification.clearAll') }}</button>
        </div>
      </PopoverPanel>
    </transition>
  </Popover>

  <!-- Toast notifications (TailwindUI pattern) - fixed top-right -->
  <div aria-live="assertive" class="pointer-events-none fixed inset-0 z-[70] flex items-end px-4 py-6 sm:items-start sm:p-6">
    <div class="flex w-full flex-col items-center space-y-3 sm:items-end">
      <transition-group
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 sm:translate-x-0"
        leave-active-class="transition ease-in duration-100"
        leave-from-class=""
        leave-to-class="opacity-0"
      >
        <div
          v-for="toast in visibleToasts"
          :key="toast.id"
          class="pointer-events-auto w-full max-w-sm rounded-lg bg-white shadow-lg outline-1 outline-black/5 dark:bg-gray-800 dark:-outline-offset-1 dark:outline-white/10"
        >
          <div class="p-4">
            <div class="flex items-start">
              <div class="shrink-0">
                <CheckCircleIcon v-if="toast.type === 'success'" class="size-6 text-green-400" aria-hidden="true" />
                <XCircleIcon v-else-if="toast.type === 'error'" class="size-6 text-red-400" aria-hidden="true" />
                <InformationCircleIcon v-else class="size-6 text-sky-400" aria-hidden="true" />
              </div>
              <div class="ml-3 w-0 flex-1 pt-0.5">
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ toast.title }}</p>
                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ toast.message }}</p>
              </div>
              <div class="ml-4 flex shrink-0">
                <button type="button" @click="dismissToast(toast.id)" class="inline-flex rounded-md text-gray-400 hover:text-gray-500 focus:outline-2 focus:outline-offset-2 focus:outline-sky-600 dark:hover:text-white dark:focus:outline-sky-500">
                  <span class="sr-only">Close</span>
                  <XMarkIcon class="size-5" aria-hidden="true" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Popover, PopoverButton, PopoverPanel } from '@headlessui/vue'
import { BellIcon } from '@heroicons/vue/24/outline'
import { CheckCircleIcon, XCircleIcon, InformationCircleIcon } from '@heroicons/vue/20/solid'
import { XMarkIcon } from '@heroicons/vue/20/solid'
import { useNotificationStore, type Notification } from '@/stores/notification'

const { t } = useI18n()
const store = useNotificationStore()

const visibleToasts = ref<Notification[]>([])
const toastTimers = new Map<string, ReturnType<typeof setTimeout>>()

watch(() => store.items.length, (newLen, oldLen) => {
  if (newLen > oldLen) {
    const latest = store.items[0]
    if (latest && !visibleToasts.value.find(t => t.id === latest.id)) {
      visibleToasts.value.push(latest)
      const timer = setTimeout(() => dismissToast(latest.id), 5000)
      toastTimers.set(latest.id, timer)
    }
  }
})

function dismissToast(id: string) {
  visibleToasts.value = visibleToasts.value.filter(t => t.id !== id)
  const timer = toastTimers.get(id)
  if (timer) {
    clearTimeout(timer)
    toastTimers.delete(id)
  }
}

function timeAgo(ts: number): string {
  const diff = Math.floor((Date.now() - ts) / 1000)
  if (diff < 60) return t('notification.justNow')
  if (diff < 3600) return t('notification.minutesAgo', { n: Math.floor(diff / 60) })
  if (diff < 86400) return t('notification.hoursAgo', { n: Math.floor(diff / 3600) })
  return t('notification.daysAgo', { n: Math.floor(diff / 86400) })
}
</script>
