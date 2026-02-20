'use client'

import { useEffect, useState } from 'react'
import AppLayout from '@/components/AppLayout'
import { useAuth } from '@/contexts/AuthContext'
import { getDocuments } from '@/lib/documents'
import { getNotifications } from '@/lib/notifications'

export default function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState({ documents: 0, notifications: 0 })

  useEffect(() => {
    async function loadStats() {
      try {
        const [docs, notifs] = await Promise.all([
          getDocuments({ page: 1, page_size: 1 }),
          getNotifications(1, 1, true)
        ])
        setStats({ documents: docs.total, notifications: notifs.unread_count })
      } catch (err) {
        console.error('Failed to load stats', err)
      }
    }
    loadStats()
  }, [])

  return (
    <AppLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Welcome</h3>
            <p className="mt-2 text-2xl font-semibold text-gray-800">{user?.full_name}</p>
            <p className="text-sm text-gray-500">{user?.role}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Total Documents</h3>
            <p className="mt-2 text-3xl font-semibold text-blue-600">{stats.documents}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Unread Notifications</h3>
            <p className="mt-2 text-3xl font-semibold text-yellow-600">{stats.notifications}</p>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
