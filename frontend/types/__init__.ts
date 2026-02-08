/**
 * Shared TypeScript types and interfaces
 */

export interface ApiError {
  success: false
  error: string
  detail?: string
  status_code: number
}

export interface ApiSuccess<T = any> {
  success: true
  message: string
  data?: T
}

export type ApiResponse<T = any> = ApiSuccess<T> | ApiError
