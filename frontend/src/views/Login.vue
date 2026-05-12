<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">DataFlow</h1>
      <p class="text-gray-500 mb-8 text-sm">可视化数据批处理系统</p>

      <div class="flex mb-6 border-b">
        <button
          class="flex-1 pb-2 text-sm font-medium transition-colors"
          :class="mode === 'login' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500'"
          @click="mode = 'login'"
        >
          登录
        </button>
        <button
          class="flex-1 pb-2 text-sm font-medium transition-colors"
          :class="mode === 'register' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-500'"
          @click="mode = 'register'"
        >
          注册
        </button>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
          <input
            v-model="form.username"
            type="text"
            required
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div v-if="mode === 'register'">
          <label class="block text-sm font-medium text-gray-700 mb-1">邮箱（可选）</label>
          <input
            v-model="form.email"
            type="email"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold py-2 rounded-lg transition-colors disabled:opacity-60"
        >
          {{ loading ? '处理中...' : mode === 'login' ? '登录' : '注册' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
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
