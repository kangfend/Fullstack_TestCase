'use client'

import { useEffect, useState } from 'react'
import AppLayout from '@/components/AppLayout'
import { useAuth } from '@/contexts/AuthContext'
import type { Notification } from '@/types'
import * as notificationsApi from '@/lib/notifications'

export default function NotificationsPage() {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [pagination, setPagination] = useState({ page: 1, totalPages: 1 })
  const [unreadOnly, setUnreadOnly] = useState(false)
  const [loading, setLoading] = useState(true)

  const loadNotifications = async () => {
    setLoading(true)
    try {
      const data = await notificationsApi.getNotifications(pagination.page, 10, unreadOnly)
      setNotifications(data.items)
      setPagination(p => ({ ...p, totalPages: data.total_pages }))
    } catch (err) {
      console.error('Failed to load notifications', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadNotifications()
  }, [pagination.page, unreadOnly])

  const handleMarkAsRead = async (id: number) => {
    try {
      await notificationsApi.markAsRead(id)
      loadNotifications()
    } catch {
      alert('Failed to mark as read')
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificationsApi.markAllAsRead()
      loadNotifications()
    } catch {
      alert('Failed to mark all as read')
    }
  }

  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleString()
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">Notifications</h1>
          <div className="flex gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={unreadOnly}
                onChange={e => { setUnreadOnly(e.target.checked); setPagination(p => ({ ...p, page: 1 })) }}
              />
              <span className="text-sm">Unread only</span>
            </label>
            <button
              onClick={handleMarkAllAsRead}
              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
            >
              Mark all as read
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No notifications</div>
        ) : (
          <div className="space-y-3">
            {notifications.map(notif => (
              <div
                key={notif.id}
                className={`bg-white p-4 rounded-lg shadow-sm ${!notif.is_read ? 'border-l-4 border-blue-500' : ''}`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-gray-800">{notif.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{notif.message}</p>
                    <p className="text-xs text-gray-400 mt-2">{formatDate(notif.created_at)}</p>
                  </div>
                  {!notif.is_read && (
                    <button
                      onClick={() => handleMarkAsRead(notif.id)}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      Mark as read
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {pagination.totalPages > 1 && (
          <div className="flex justify-center gap-2">
            <button
              onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))}
              disabled={pagination.page <= 1}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-3 py-1">
              Page {pagination.page} of {pagination.totalPages}
            </span>
            <button
              onClick={() => setPagination(p => ({ ...p, page: p.page + 1 }))}
              disabled={pagination.page >= pagination.totalPages}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
