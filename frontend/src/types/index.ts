export interface User {
  id: number
  email: string
  full_name: string
  role: 'ADMIN' | 'USER'
  is_active: boolean
  created_at: string
}

export interface Document {
  id: number
  title: string
  description: string | null
  document_type: string
  file_url: string
  file_name: string
  file_size: number
  status: 'ACTIVE' | 'PENDING_DELETE' | 'PENDING_REPLACE' | 'DELETED'
  version: number
  created_by: number
  created_by_name: string | null
  created_at: string
  updated_at: string
}

export interface PermissionRequest {
  id: number
  document_id: number
  requested_by: number
  request_type: 'DELETE' | 'REPLACE'
  reason: string | null
  new_file_url: string | null
  status: 'PENDING' | 'APPROVED' | 'REJECTED'
  reviewed_by: number | null
  reviewed_at: string | null
  created_at: string
  document?: Document
}

export interface Notification {
  id: number
  user_id: number
  title: string
  message: string
  is_read: boolean
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface NotificationListResponse extends PaginatedResponse<Notification> {
  unread_count: number
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  full_name: string
  password: string
}

export interface DocumentFilters {
  search?: string
  document_type?: string
  status?: string
  page?: number
  page_size?: number
}
