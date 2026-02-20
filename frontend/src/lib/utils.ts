/**
 * Format file size from bytes to human readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

/**
 * Format date string to localized date and time
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString()
}

/**
 * Get status badge color classes for Tailwind
 */
export function getStatusBadge(status: string): string {
  const colors: Record<string, string> = {
    ACTIVE: 'bg-green-100 text-green-800',
    PENDING_DELETE: 'bg-yellow-100 text-yellow-800',
    PENDING_REPLACE: 'bg-blue-100 text-blue-800',
    DELETED: 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

/**
 * Format status text for display (replace underscores with spaces)
 */
export function formatStatus(status: string): string {
  return status.replace(/_/g, ' ')
}
