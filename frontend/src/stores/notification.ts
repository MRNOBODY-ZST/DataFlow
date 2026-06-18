import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { notificationApi, type NotificationItem } from '@/api/notification'

export type { NotificationItem as Notification }

export const useNotificationStore = defineStore('notification', () => {
  const items = ref<NotificationItem[]>([])
  const loading = ref(false)

  const unreadCount = computed(() => items.value.filter(n => !n.read).length)

  async function fetchAll() {
    loading.value = true
    try {
      const { data } = await notificationApi.list()
      items.value = data
    } finally {
      loading.value = false
    }
  }

  async function add(type: NotificationItem['type'], title: string, message: string) {
    // Optimistic local insert for immediate toast feedback; backend creates the
    // persistent record (e.g. via Kafka consumer). Next fetchAll syncs the list.
    items.value.unshift({
      id: -Date.now(),
      type,
      title,
      message,
      read: false,
      createdAt: new Date().toISOString(),
    })
    if (items.value.length > 50) items.value.length = 50
  }

  async function markRead(id: number) {
    const n = items.value.find(i => i.id === id)
    if (n) n.read = true
    if (id > 0) {
      await notificationApi.markRead(id).catch(() => {})
    }
  }

  async function markAllRead() {
    items.value.forEach(n => { n.read = true })
    await notificationApi.markAllRead().catch(() => {})
  }

  async function remove(id: number) {
    items.value = items.value.filter(i => i.id !== id)
    if (id > 0) {
      await notificationApi.remove(id).catch(() => {})
    }
  }

  async function clearAll() {
    items.value = []
    await notificationApi.clearAll().catch(() => {})
  }

  return { items, loading, unreadCount, fetchAll, add, markRead, markAllRead, remove, clearAll }
})
