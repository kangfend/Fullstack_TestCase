import api from './api'
import type { Document, PaginatedResponse, DocumentFilters, PermissionRequest } from '@/types'

export async function getDocuments(filters: DocumentFilters = {}): Promise<PaginatedResponse<Document>> {
  const params = new URLSearchParams()
  if (filters.search) params.append('search', filters.search)
  if (filters.document_type) params.append('document_type', filters.document_type)
  if (filters.status) params.append('status', filters.status)
  params.append('page', String(filters.page || 1))
  params.append('page_size', String(filters.page_size || 10))
  
  const response = await api.get(`/documents/?${params.toString()}`)
  return response.data
}

export async function getDocument(documentId: number): Promise<Document> {
  const response = await api.get(`/documents/${documentId}`)
  return response.data
}

export async function uploadDocument(data: FormData): Promise<Document> {
  const response = await api.post('/documents/upload', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function getDownloadUrl(documentId: number): Promise<string> {
  const response = await api.get(`/documents/${documentId}/download-url`)
  return response.data.download_url
}

export async function requestDelete(documentId: number, reason?: string): Promise<PermissionRequest> {
  const formData = new FormData()
  if (reason) formData.append('reason', reason)
  const response = await api.post(`/documents/${documentId}/request-delete`, formData)
  return response.data
}

export async function requestReplace(documentId: number, file: File, reason?: string): Promise<PermissionRequest> {
  const formData = new FormData()
  formData.append('file', file)
  if (reason) formData.append('reason', reason)
  const response = await api.post(`/documents/${documentId}/request-replace`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function adminDeleteDocument(documentId: number): Promise<void> {
  await api.delete(`/documents/${documentId}`)
}

export async function adminReplaceDocument(documentId: number, file: File): Promise<Document> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post(`/documents/${documentId}/replace`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function getPendingRequests(page = 1, pageSize = 10): Promise<PaginatedResponse<PermissionRequest>> {
  const response = await api.get(`/documents/permissions/pending?page=${page}&page_size=${pageSize}`)
  return response.data
}

export async function approveRequest(requestId: number): Promise<PermissionRequest> {
  const response = await api.post(`/documents/permissions/${requestId}/approve`)
  return response.data
}

export async function rejectRequest(requestId: number): Promise<PermissionRequest> {
  const response = await api.post(`/documents/permissions/${requestId}/reject`)
  return response.data
}
