/**
 * User TypeScript interfaces for authentication and user management
 */

export interface User {
  id: string
  email: string
  name?: string
  emailVerified: boolean
  image?: string
  createdAt: string
  updatedAt: string
}

export interface UserCreate {
  email: string
  password: string
  name?: string
}

export interface UserLogin {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface AuthSession {
  user: User
  token: string
  expiresAt: number
}
