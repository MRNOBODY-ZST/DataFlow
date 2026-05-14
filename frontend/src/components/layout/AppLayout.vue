<template>
  <div>
    <TransitionRoot as="template" :show="sidebarOpen">
      <Dialog class="relative z-50 lg:hidden" @close="sidebarOpen = false">
        <TransitionChild as="template" enter="transition-opacity ease-linear duration-300" enter-from="opacity-0" enter-to="" leave="transition-opacity ease-linear duration-300" leave-from="" leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-900/80"></div>
        </TransitionChild>

        <div class="fixed inset-0 flex">
          <TransitionChild as="template" enter="transition ease-in-out duration-300 transform" enter-from="-translate-x-full" enter-to="translate-x-0" leave="transition ease-in-out duration-300 transform" leave-from="translate-x-0" leave-to="-translate-x-full">
            <DialogPanel class="relative mr-16 flex w-full max-w-xs flex-1">
              <TransitionChild as="template" enter="ease-in-out duration-300" enter-from="opacity-0" enter-to="" leave="ease-in-out duration-300" leave-from="" leave-to="opacity-0">
                <div class="absolute top-0 left-full flex w-16 justify-center pt-5">
                  <button type="button" class="-m-2.5 p-2.5" @click="sidebarOpen = false">
                    <span class="sr-only">Close sidebar</span>
                    <XMarkIcon class="size-6 text-white" aria-hidden="true" />
                  </button>
                </div>
              </TransitionChild>

              <div class="relative flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 dark:bg-gray-900 dark:ring dark:ring-white/10 dark:before:pointer-events-none dark:before:absolute dark:before:inset-0 dark:before:bg-black/10">
                <div class="relative flex h-16 shrink-0 items-center gap-2">
                  <img src="/DataFlow.svg" alt="DataFlow" class="h-8 w-8" />
                  <span class="text-xl font-bold text-sky-600 dark:text-sky-400">DataFlow</span>
                </div>
                <nav class="relative flex flex-1 flex-col">
                  <ul role="list" class="flex flex-1 flex-col gap-y-7">
                    <li>
                      <ul role="list" class="-mx-2 space-y-1">
                        <li v-for="item in navigation" :key="item.key">
                          <router-link :to="item.href" :class="[item.current ? 'bg-gray-50 text-sky-600 dark:bg-white/5 dark:text-white' : 'text-gray-700 hover:bg-gray-50 hover:text-sky-600 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-white', 'group flex gap-x-3 rounded-md p-2 text-sm/6 font-semibold']">
                            <component :is="item.icon" :class="[item.current ? 'text-sky-600 dark:text-white' : 'text-gray-400 group-hover:text-sky-600 dark:group-hover:text-white', 'size-6 shrink-0']" aria-hidden="true" />
                            {{ item.name }}
                          </router-link>
                        </li>
                      </ul>
                    </li>
                    <li class="mt-auto">
                      <router-link to="/settings" class="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm/6 font-semibold text-gray-700 hover:bg-gray-50 hover:text-sky-600 dark:text-gray-300 dark:hover:bg-white/5 dark:hover:text-white">
                        <Cog6ToothIcon class="size-6 shrink-0 text-gray-400 group-hover:text-sky-600 dark:group-hover:text-white" aria-hidden="true" />
                        {{ t('nav.settings') }}
                      </router-link>
                    </li>
                  </ul>
                </nav>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </TransitionRoot>

    <div class="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
      <div class="flex grow flex-col gap-y-5 overflow-y-auto border-r border-gray-200 bg-white px-6 pb-4 dark:border-white/10 dark:bg-gray-900">
        <div class="flex h-16 shrink-0 items-center gap-2">
          <img src="/DataFlow.svg" alt="DataFlow" class="h-8 w-8" />
          <span class="text-xl font-bold text-sky-600 dark:text-sky-400">DataFlow</span>
        </div>
        <nav class="flex flex-1 flex-col">
          <ul role="list" class="flex flex-1 flex-col gap-y-7">
            <li>
              <ul role="list" class="-mx-2 space-y-1">
                <li v-for="item in navigation" :key="item.key">
                  <router-link :to="item.href" :class="[item.current ? 'bg-gray-50 text-sky-600 dark:bg-white/5 dark:text-white' : 'text-gray-700 hover:bg-gray-50 hover:text-sky-600 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-white', 'group flex gap-x-3 rounded-md p-2 text-sm/6 font-semibold']">
                    <component :is="item.icon" :class="[item.current ? 'text-sky-600 dark:text-white' : 'text-gray-400 group-hover:text-sky-600 dark:group-hover:text-white', 'size-6 shrink-0']" aria-hidden="true" />
                    {{ item.name }}
                  </router-link>
                </li>
              </ul>
            </li>
            <li class="mt-auto">
              <router-link to="/settings" class="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm/6 font-semibold text-gray-700 hover:bg-gray-50 hover:text-sky-600 dark:text-gray-300 dark:hover:bg-white/5 dark:hover:text-white">
                <Cog6ToothIcon class="size-6 shrink-0 text-gray-400 group-hover:text-sky-600 dark:group-hover:text-white" aria-hidden="true" />
                {{ t('nav.settings') }}
              </router-link>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <div class="lg:pl-72">
      <div class="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-xs sm:gap-x-6 sm:px-6 lg:px-8 dark:border-white/10 dark:bg-gray-900 dark:shadow-none">
        <button type="button" class="-m-2.5 p-2.5 text-gray-700 hover:text-gray-900 lg:hidden dark:text-gray-400 dark:hover:text-white" @click="sidebarOpen = true">
          <span class="sr-only">Open sidebar</span>
          <Bars3Icon class="size-6" aria-hidden="true" />
        </button>

        <div class="h-6 w-px bg-gray-200 lg:hidden dark:bg-white/10" aria-hidden="true"></div>

        <div class="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
          <form class="grid flex-1 grid-cols-1" action="#" method="GET" @submit.prevent>
            <input name="search" aria-label="Search" class="col-start-1 row-start-1 block size-full bg-white pl-8 text-base text-gray-900 outline-hidden placeholder:text-gray-400 sm:text-sm/6 dark:bg-gray-900 dark:text-white dark:placeholder:text-gray-500" :placeholder="t('common.search')" />
            <MagnifyingGlassIcon class="pointer-events-none col-start-1 row-start-1 size-5 self-center text-gray-400" aria-hidden="true" />
          </form>
          <div class="flex items-center gap-x-4 lg:gap-x-6">
            <button type="button" class="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500 dark:hover:text-white">
              <span class="sr-only">View notifications</span>
              <BellIcon class="size-6" aria-hidden="true" />
            </button>

            <div class="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200 dark:lg:bg-white/10" aria-hidden="true"></div>

            <Menu as="div" class="relative">
              <MenuButton class="relative flex items-center">
                <span class="absolute -inset-1.5"></span>
                <span class="sr-only">Open user menu</span>
                <span class="flex size-8 items-center justify-center rounded-full bg-sky-500 text-sm font-semibold text-white">{{ initials }}</span>
                <span class="hidden lg:flex lg:items-center">
                  <span class="ml-4 text-sm/6 font-semibold text-gray-900 dark:text-white" aria-hidden="true">{{ auth.username || t('common.user') }}</span>
                  <ChevronDownIcon class="ml-2 size-5 text-gray-400 dark:text-gray-500" aria-hidden="true" />
                </span>
              </MenuButton>
              <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="transform scale-100" leave-to-class="transform opacity-0 scale-95">
                <MenuItems class="absolute right-0 z-10 mt-2.5 w-32 origin-top-right rounded-md bg-white py-2 shadow-lg outline-1 outline-gray-900/5 dark:bg-gray-800 dark:shadow-none dark:-outline-offset-1 dark:outline-white/10">
                  <MenuItem v-slot="{ active }">
                    <button type="button" :class="[active ? 'bg-gray-50 outline-hidden dark:bg-white/5' : '', 'block w-full px-3 py-1 text-left text-sm/6 text-gray-900 dark:text-white']" @click="logout">{{ t('common.signOut') }}</button>
                  </MenuItem>
                </MenuItems>
              </transition>
            </Menu>
          </div>
        </div>
      </div>

      <main>
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Dialog,
  DialogPanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import {
  Bars3Icon,
  BellIcon,
  Cog6ToothIcon,
  FolderIcon,
  HomeIcon,
  RectangleGroupIcon,
  ClipboardDocumentListIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'
import { ChevronDownIcon, MagnifyingGlassIcon } from '@heroicons/vue/20/solid'
import { useAuthStore } from '@/stores/auth'

defineProps<{ title?: string }>()

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const sidebarOpen = ref(false)

const navigation = computed(() => [
  { key: 'dashboard', name: t('nav.dashboard'), href: '/dashboard', icon: HomeIcon, current: route.path === '/dashboard' },
  { key: 'pipeline', name: t('nav.pipeline'), href: '/pipelines', icon: RectangleGroupIcon, current: route.path.startsWith('/pipelines') || route.path.startsWith('/editor') },
  { key: 'files', name: t('nav.files'), href: '/files', icon: FolderIcon, current: route.path.startsWith('/files') },
  { key: 'tasks', name: t('nav.tasks'), href: '/tasks', icon: ClipboardDocumentListIcon, current: route.path.startsWith('/tasks') },
])

const initials = computed(() => (auth.username?.slice(0, 1) || 'U').toUpperCase())

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
