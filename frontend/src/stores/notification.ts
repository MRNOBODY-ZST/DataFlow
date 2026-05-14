import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'info'
  title: string
  message: string
  time: number
  read: boolean
}

export const useNotificationStore = defineStore('notification', () => {
  const items = ref<Notification[]>([])

  const unreadCount = computed(() => items.value.filter(n => !n.read).length)

  function add(type: Notification['type'], title: string, message: string) {
    items.value.unshift({
      id: `${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      type,
      title,
      message,
      time: Date.now(),
      read: false,
    })
    if (items.value.length > 50) items.value.length = 50
  }

  function markRead(id: string) {
    const n = items.value.find(i => i.id === id)
    if (n) n.read = true
  }

  function markAllRead() {
    items.value.forEach(n => { n.read = true })
  }

  function remove(id: string) {
    items.value = items.value.filter(i => i.id !== id)
  }

  function clearAll() {
    items.value = []
  }

  return { items, unreadCount, add, markRead, markAllRead, remove, clearAll }
})
