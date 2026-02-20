import api from './api'
import type { NotificationListResponse } from '@/types'

export async function getNotifications(
  page = 1,
  pageSize = 10,
  unreadOnly = false
): Promise<NotificationListResponse> {
  const response = await api.get(
    `/notifications/?page=${page}&page_size=${pageSize}&unread_only=${unreadOnly}`
  )
  return response.data
}

export async function markAsRead(notificationId: number): Promise<void> {
  await api.patch(`/notifications/${notificationId}/read`)
}

export async function markAllAsRead(): Promise<void> {
  await api.patch('/notifications/read-all')
}
