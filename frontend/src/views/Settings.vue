<template>
  <AppLayout title="Settings">
    <div class="py-6 px-4 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-2xl">
        <div class="space-y-10">
          <!-- Profile Section -->
          <div class="border-b border-gray-200 pb-10 dark:border-white/10">
            <h2 class="text-base font-semibold text-gray-900 dark:text-white">Profile</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Your account information.</p>

            <dl class="mt-6 divide-y divide-gray-200 dark:divide-white/10">
              <div class="py-4 sm:grid sm:grid-cols-3 sm:gap-4">
                <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">Username</dt>
                <dd class="mt-1 text-sm text-gray-700 sm:col-span-2 sm:mt-0 dark:text-gray-300">{{ auth.username || '—' }}</dd>
              </div>
              <div class="py-4 sm:grid sm:grid-cols-3 sm:gap-4">
                <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">User ID</dt>
                <dd class="mt-1 text-sm text-gray-700 sm:col-span-2 sm:mt-0 dark:text-gray-300">{{ auth.userId || '—' }}</dd>
              </div>
            </dl>
          </div>

          <!-- Appearance Section -->
          <div class="border-b border-gray-200 pb-10 dark:border-white/10">
            <h2 class="text-base font-semibold text-gray-900 dark:text-white">Appearance</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Customize how the app looks.</p>

            <div class="mt-6">
              <fieldset>
                <legend class="text-sm font-medium text-gray-900 dark:text-gray-100">Theme</legend>
                <div class="mt-4 space-y-3">
                  <div v-for="option in themeOptions" :key="option.value" class="flex items-center gap-3">
                    <div class="group grid size-4 grid-cols-1">
                      <input
                        :id="`theme-${option.value}`"
                        v-model="theme"
                        type="radio"
                        :value="option.value"
                        class="col-start-1 row-start-1 appearance-none rounded-full border border-gray-300 bg-white checked:border-indigo-600 checked:bg-indigo-600 dark:border-white/10 dark:bg-white/5 dark:checked:border-indigo-500 dark:checked:bg-indigo-500"
                        @change="applyTheme"
                      />
                    </div>
                    <label :for="`theme-${option.value}`" class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ option.label }}</label>
                  </div>
                </div>
              </fieldset>
            </div>
          </div>

          <!-- API Section -->
          <div class="pb-10">
            <h2 class="text-base font-semibold text-gray-900 dark:text-white">API Configuration</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Backend connection settings.</p>

            <dl class="mt-6 divide-y divide-gray-200 dark:divide-white/10">
              <div class="py-4 sm:grid sm:grid-cols-3 sm:gap-4">
                <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">API Base URL</dt>
                <dd class="mt-1 text-sm text-gray-700 sm:col-span-2 sm:mt-0 dark:text-gray-300">/api</dd>
              </div>
              <div class="py-4 sm:grid sm:grid-cols-3 sm:gap-4">
                <dt class="text-sm font-medium text-gray-900 dark:text-gray-100">Auth Token</dt>
                <dd class="mt-1 text-sm sm:col-span-2 sm:mt-0">
                  <span class="font-mono text-xs text-gray-400 dark:text-gray-500">{{ maskedToken }}</span>
                </dd>
              </div>
            </dl>
          </div>

          <!-- Danger Zone -->
          <div class="rounded-lg border border-red-200 p-6 dark:border-red-500/20">
            <h2 class="text-base font-semibold text-red-600 dark:text-red-400">Danger Zone</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Irreversible actions.</p>
            <div class="mt-4">
              <button type="button" class="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-red-500 dark:bg-red-500 dark:hover:bg-red-400" @click="logout">Sign Out</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const themeOptions = [
  { label: 'System', value: 'system' },
  { label: 'Light', value: 'light' },
  { label: 'Dark', value: 'dark' },
]

const theme = ref(localStorage.getItem('df_theme') || 'system')

const maskedToken = computed(() => {
  if (!auth.token) return '—'
  return auth.token.slice(0, 8) + '...' + auth.token.slice(-4)
})

function applyTheme() {
  localStorage.setItem('df_theme', theme.value)
  const html = document.documentElement
  if (theme.value === 'dark') {
    html.classList.add('dark')
  } else if (theme.value === 'light') {
    html.classList.remove('dark')
  } else {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
