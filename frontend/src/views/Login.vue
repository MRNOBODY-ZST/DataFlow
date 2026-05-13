<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <div class="rounded-lg bg-white px-6 py-10 shadow-sm ring-1 ring-gray-900/5 sm:px-10">
        <div class="sm:mx-auto sm:w-full sm:max-w-sm">
          <h1 class="text-center text-3xl font-bold tracking-tight text-gray-900">DataFlow</h1>
          <p class="mt-2 text-center text-sm text-gray-500">可视化数据批处理系统</p>
        </div>

        <div class="mt-8 flex border-b border-gray-200">
          <button class="flex-1 border-b-2 px-2 pb-3 text-sm font-medium transition-colors" :class="mode === 'login' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'" @click="mode = 'login'">登录</button>
          <button class="flex-1 border-b-2 px-2 pb-3 text-sm font-medium transition-colors" :class="mode === 'register' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'" @click="mode = 'register'">注册</button>
        </div>

        <form class="mt-8 space-y-6" @submit.prevent="submit">
          <div>
            <label class="block text-sm font-medium text-gray-900">用户名</label>
            <div class="mt-2">
              <input v-model="form.username" type="text" required class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6" />
            </div>
          </div>

          <div v-if="mode === 'register'">
            <label class="block text-sm font-medium text-gray-900">邮箱（可选）</label>
            <div class="mt-2">
              <input v-model="form.email" type="email" class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-900">密码</label>
            <div class="mt-2">
              <input v-model="form.password" type="password" required class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6" />
            </div>
          </div>

          <div v-if="error" class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</div>

          <button type="submit" :disabled="loading" class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-60">
            {{ loading ? '处理中...' : mode === 'login' ? '登录' : '注册' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const mode = ref<'login' | 'register'>('login')
const loading = ref(false)
const error = ref('')
const form = reactive({ username: '', password: '', email: '' })

async function submit() {
  error.value = ''
  loading.value = true
  try {
    if (mode.value === 'login') {
      await auth.login(form.username, form.password)
    } else {
      await auth.register(form.username, form.password, form.email || undefined)
    }
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.message || e.message || '操作失败'
  } finally {
    loading.value = false
  }
}
</script>
