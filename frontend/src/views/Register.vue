<template>
  <div class="flex min-h-full flex-1">
    <div class="flex flex-1 flex-col justify-center px-4 py-12 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
      <div class="mx-auto w-full max-w-sm lg:w-96">
        <div>
          <h1 class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">DataFlow</h1>
          <h2 class="mt-8 text-2xl/9 font-bold tracking-tight text-gray-900 dark:text-white">{{ t('auth.createAccountTitle') }}</h2>
          <p class="mt-2 text-sm/6 text-gray-500 dark:text-gray-400">
            {{ t('auth.hasAccount') }}
            {{ ' ' }}
            <router-link to="/login" class="font-semibold text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300">{{ t('auth.signInLink') }}</router-link>
          </p>
        </div>

        <div class="mt-10">
          <form class="space-y-6" @submit.prevent="submit">
            <div>
              <label for="username" class="block text-sm/6 font-medium text-gray-900 dark:text-gray-100">{{ t('auth.username') }}</label>
              <div class="mt-2">
                <input v-model="form.username" type="text" id="username" autocomplete="username" required class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500" />
              </div>
            </div>

            <div>
              <label for="email" class="block text-sm/6 font-medium text-gray-900 dark:text-gray-100">{{ t('auth.email') }}</label>
              <div class="mt-2">
                <input v-model="form.email" type="email" id="email" autocomplete="email" class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500" />
              </div>
            </div>

            <div>
              <label for="password" class="block text-sm/6 font-medium text-gray-900 dark:text-gray-100">{{ t('auth.password') }}</label>
              <div class="mt-2">
                <input v-model="form.password" type="password" id="password" autocomplete="new-password" required class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6 dark:bg-white/5 dark:text-white dark:outline-white/10 dark:placeholder:text-gray-500 dark:focus:outline-indigo-500" />
              </div>
            </div>

            <div v-if="error" class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-400/10 dark:text-red-400">{{ error }}</div>

            <div>
              <button type="submit" :disabled="loading" class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm/6 font-semibold text-white shadow-xs hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-60 dark:bg-indigo-500 dark:shadow-none dark:hover:bg-indigo-400 dark:focus-visible:outline-indigo-500">
                {{ loading ? t('auth.creatingAccount') : t('auth.createAccount') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div class="relative hidden w-0 flex-1 lg:block">
      <div class="absolute inset-0 bg-linear-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
        <div class="text-center text-white px-12">
          <RectangleGroupIcon class="mx-auto size-20 opacity-80" />
          <h2 class="mt-6 text-3xl font-bold">{{ t('auth.heroTitle') }}</h2>
          <p class="mt-4 text-lg opacity-80">{{ t('auth.heroDesc') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { RectangleGroupIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()

const loading = ref(false)
const error = ref('')
const form = reactive({ username: '', password: '', email: '' })

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(form.username, form.password, form.email || undefined)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.message || e.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
