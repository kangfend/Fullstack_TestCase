'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
import { useAuth } from '@/contexts/AuthContext'
import type { PermissionRequest } from '@/types'
import * as documentsApi from '@/lib/documents'

export default function AdminRequestsPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [requests, setRequests] = useState<PermissionRequest[]>([])
  const [pagination, setPagination] = useState({ page: 1, totalPages: 1 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && user?.role !== 'ADMIN') {
      router.push('/dashboard')
    }
  }, [user, authLoading, router])

  const loadRequests = async () => {
    setLoading(true)
    try {
      const data = await documentsApi.getPendingRequests(pagination.page, 10)
      setRequests(data.items)
      setPagination(p => ({ ...p, totalPages: data.total_pages }))
    } catch (err) {
      console.error('Failed to load requests', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user?.role === 'ADMIN') {
      loadRequests()
    }
  }, [pagination.page, user])

  const handleApprove = async (id: number) => {
    if (!confirm('Approve this request?')) return
    try {
      await documentsApi.approveRequest(id)
      loadRequests()
    } catch {
      alert('Failed to approve request')
    }
  }

  const handleReject = async (id: number) => {
    if (!confirm('Reject this request?')) return
    try {
      await documentsApi.rejectRequest(id)
      loadRequests()
    } catch {
      alert('Failed to reject request')
    }
  }

  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleString()
  }

  if (authLoading || user?.role !== 'ADMIN') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-800">Pending Requests</h1>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : requests.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No pending requests</div>
        ) : (
          <div className="space-y-4">
            {requests.map(req => (
              <div key={req.id} className="bg-white p-4 rounded-lg shadow-sm">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                        req.request_type === 'DELETE' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {req.request_type}
                      </span>
                      <span className="text-sm text-gray-500">Document ID: {req.document_id}</span>
                    </div>
                    {req.reason && (
                      <p className="text-sm text-gray-600 mt-2">
                        <span className="font-medium">Reason:</span> {req.reason}
                      </p>
                    )}
                    <p className="text-xs text-gray-400 mt-2">
                      Requested: {formatDate(req.created_at)}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleApprove(req.id)}
                      className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(req.id)}
                      className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                    >
                      Reject
                    </button>
                  </div>
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
