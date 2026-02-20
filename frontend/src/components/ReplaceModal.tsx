'use client'

import { useState, useRef } from 'react'

const ALLOWED_EXTENSIONS = [
  '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
  '.txt', '.rtf', '.odt', '.ods', '.odp', '.csv'
]

const ACCEPT_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'text/plain',
  'application/rtf',
  'application/vnd.oasis.opendocument.text',
  'application/vnd.oasis.opendocument.spreadsheet',
  'application/vnd.oasis.opendocument.presentation',
  'text/csv',
  '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
  '.txt', '.rtf', '.odt', '.ods', '.odp', '.csv'
].join(',')

interface ReplaceModalProps {
  isOpen: boolean
  documentId: number | null
  onClose: () => void
  onReplace: (documentId: number, file: File) => Promise<void>
}

export default function ReplaceModal({ isOpen, documentId, onClose, onReplace }: ReplaceModalProps) {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  if (!isOpen || !documentId) return null

  const validateFile = (file: File): boolean => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setError(`Invalid file type. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`)
      return false
    }
    return true
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && validateFile(selectedFile)) {
      setFile(selectedFile)
      setError('')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setError('')

    try {
      await onReplace(documentId, file)
      resetForm()
      onClose()
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Replace failed. Please try again.'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFile(null)
    setError('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">Replace Document</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">New File *</label>
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileChange}
              accept={ACCEPT_TYPES}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Allowed: PDF, DOC, XLS, PPT, TXT, RTF, ODT, CSV
            </p>
          </div>
          
          {error && <p className="text-red-500 text-sm">{error}</p>}
          
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => { resetForm(); onClose() }}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50"
            >
              {loading ? 'Replacing...' : 'Replace'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
