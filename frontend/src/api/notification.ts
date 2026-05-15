import http from './http'

export interface NotificationItem {
  id: number
  type: 'success' | 'error' | 'info'
  title: string
  message: string
  read: boolean
  createdAt: string
}

export const notificationApi = {
  list: () => http.get<NotificationItem[]>('/notifications'),

  unreadCount: () => http.get<number>('/notifications/unread-count'),

  markRead: (id: number) => http.patch<NotificationItem>(`/notifications/${id}/read`),

  markAllRead: () => http.patch<void>('/notifications/read-all'),

  remove: (id: number) => http.delete<void>(`/notifications/${id}`),

  clearAll: () => http.delete<void>('/notifications'),
}
