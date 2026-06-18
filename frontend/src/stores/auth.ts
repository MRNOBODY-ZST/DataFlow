import { ref } from 'vue'
import { defineStore } from 'pinia'
import { authApi, type AuthResponse } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('df_token'))
  const username = ref<string | null>(localStorage.getItem('df_username'))
  const userId = ref<number | null>(Number(localStorage.getItem('df_userId')) || null)

  function setAuth(res: AuthResponse) {
    token.value = res.token
    username.value = res.username
    userId.value = res.userId
    localStorage.setItem('df_token', res.token)
    localStorage.setItem('df_username', res.username)
    localStorage.setItem('df_userId', String(res.userId))
  }

  function logout() {
    token.value = null
    username.value = null
    userId.value = null
    localStorage.removeItem('df_token')
    localStorage.removeItem('df_username')
    localStorage.removeItem('df_userId')
  }

  async function login(username: string, password: string) {
    const { data } = await authApi.login(username, password)
    setAuth(data)
  }

  async function register(username: string, password: string, email?: string) {
    const { data } = await authApi.register(username, password, email)
    setAuth(data)
  }

  return { token, username, userId, login, register, logout }
})
