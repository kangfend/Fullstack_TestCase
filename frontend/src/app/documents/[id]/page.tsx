'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
import ReplaceModal from '@/components/ReplaceModal'
import RequestReplaceModal from '@/components/RequestReplaceModal'
import RequestDeleteModal from '@/components/RequestDeleteModal'
import { useAuth } from '@/contexts/AuthContext'
import type { Document } from '@/types'
import * as documentsApi from '@/lib/documents'
import { formatDate, formatFileSize, getStatusBadge, formatStatus } from '@/lib/utils'

export default function DocumentDetailPage() {
  const { user } = useAuth()
  const router = useRouter()
  const params = useParams()
  const documentId = Number(params.id)

  const [document, setDocument] = useState<Document | null>(null)
  const [loading, setLoading] = useState(true)
  const [replaceModalOpen, setReplaceModalOpen] = useState(false)
  const [requestReplaceModalOpen, setRequestReplaceModalOpen] = useState(false)
  const [requestDeleteModalOpen, setRequestDeleteModalOpen] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  const isOwner = document?.created_by === user?.id
  const isAdmin = user?.role === 'ADMIN'

  const loadDocument = async () => {
    setLoading(true)
    try {
      const data = await documentsApi.getDocument(documentId)
      setDocument(data)
    } catch (err) {
      console.error('Failed to load document', err)
      alert('Failed to load document')
      router.push('/documents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDocument()
  }, [documentId])

  const handleDownload = async () => {
    try {
      const url = await documentsApi.getDownloadUrl(documentId)
      window.open(url, '_blank')
    } catch (err) {
      alert('Failed to get download URL')
    }
  }

  const handleRequestDeleteSubmit = async (reason: string) => {
    await documentsApi.requestDelete(documentId, reason || undefined)
    setSuccessMessage('Delete request submitted successfully')
    setTimeout(() => setSuccessMessage(''), 5000)
    loadDocument()
  }

  const handleRequestReplaceSubmit = async (file: File, reason: string) => {
    await documentsApi.requestReplace(documentId, file, reason || undefined)
    setSuccessMessage('Replace request submitted successfully')
    setTimeout(() => setSuccessMessage(''), 5000)
    loadDocument()
  }

  const handleAdminDelete = async () => {
    if (!confirm('Are you sure you want to delete this document?')) return
    try {
      await documentsApi.adminDeleteDocument(documentId)
      alert('Document deleted')
      router.push('/documents')
    } catch {
      alert('Failed to delete document')
    }
  }

  const handleAdminReplace = async (id: number, file: File) => {
    await documentsApi.adminReplaceDocument(id, file)
    setSuccessMessage('Document replaced successfully')
    setTimeout(() => setSuccessMessage(''), 5000)
    loadDocument()
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="text-center py-8 text-gray-500">Loading...</div>
      </AppLayout>
    )
  }

  if (!document) {
    return (
      <AppLayout>
        <div className="text-center py-8 text-gray-500">Document not found</div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="text-gray-600 hover:text-gray-800"
          >
            ← Back
          </button>
        </div>

        {successMessage && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative">
            <span className="block sm:inline">{successMessage}</span>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">{document.title}</h1>
              {document.description && (
                <p className="text-gray-600 mt-2">{document.description}</p>
              )}
            </div>
            <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getStatusBadge(document.status)}`}>
              {formatStatus(document.status)}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 border-t pt-4">
            <div>
              <p className="text-sm text-gray-500">File Name</p>
              <p className="font-medium">{document.file_name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">File Size</p>
              <p className="font-medium">{formatFileSize(document.file_size)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Document Type</p>
              <p className="font-medium">{document.document_type}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Version</p>
              <p className="font-medium">v{document.version}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Created By</p>
              <p className="font-medium">{document.created_by_name || 'Unknown'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Created At</p>
              <p className="font-medium">{formatDate(document.created_at)}</p>
            </div>
            <div className="col-span-2">
              <p className="text-sm text-gray-500">Last Updated</p>
              <p className="font-medium">{document.updated_at ? formatDate(document.updated_at) : formatDate(document.created_at)}</p>
            </div>
          </div>

          <div className="flex gap-3 border-t pt-4">
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Download
            </button>

            {isOwner && document.status === 'ACTIVE' && (
              <>
                <button
                  onClick={() => setRequestDeleteModalOpen(true)}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Request Delete
                </button>
                <button
                  onClick={() => setRequestReplaceModalOpen(true)}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700"
                >
                  Request Replace
                </button>
              </>
            )}

            {isAdmin && (
              <>
                <button
                  onClick={handleAdminDelete}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Delete (Admin)
                </button>
                <button
                  onClick={() => setReplaceModalOpen(true)}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700"
                >
                  Replace (Admin)
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      <ReplaceModal
        isOpen={replaceModalOpen}
        documentId={documentId}
        onClose={() => setReplaceModalOpen(false)}
        onReplace={handleAdminReplace}
      />

      <RequestReplaceModal
        isOpen={requestReplaceModalOpen}
        onClose={() => setRequestReplaceModalOpen(false)}
        onSubmit={handleRequestReplaceSubmit}
      />

      <RequestDeleteModal
        isOpen={requestDeleteModalOpen}
        onClose={() => setRequestDeleteModalOpen(false)}
        onSubmit={handleRequestDeleteSubmit}
      />
    </AppLayout>
  )
}
