/**
 * JWT authentication client for backend API
 * Simplified config without BetterAuth database dependency
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

/**
 * Token storage helper (client-side only)
 */
const TOKEN_KEY = 'auth_token'

function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

function setToken(token: string): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(TOKEN_KEY, token)
}

function removeToken(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(TOKEN_KEY)
}

/**
 * Custom auth client for API calls to backend
 */
export const authClient = {
  /**
   * Sign up a new user
   */
  async signup(email: string, password: string, name?: string) {
    const response = await fetch(`${BACKEND_URL}/api/auth/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password, name }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Signup failed")
    }

    const data = await response.json()
    // Store the JWT token
    if (data.access_token) {
      setToken(data.access_token)
    }
    return data
  },

  /**
   * Sign in an existing user
   */
  async signin(email: string, password: string) {
    const response = await fetch(`${BACKEND_URL}/api/auth/signin`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Signin failed")
    }

    const data = await response.json()
    // Store the JWT token
    if (data.access_token) {
      setToken(data.access_token)
    }
    return data
  },

  /**
   * Sign out the current user
   */
  async signout() {
    const token = getToken()
    const response = await fetch(`${BACKEND_URL}/api/auth/signout`, {
      method: "POST",
      headers: token ? {
        "Authorization": `Bearer ${token}`,
      } : {},
      credentials: "include",
    })

    // Remove token regardless of response
    removeToken()

    if (!response.ok) {
      throw new Error("Signout failed")
    }

    return response.json()
  },

  /**
   * Get the current user session
   */
  async getSession() {
    const token = getToken()

    if (!token) {
      return null
    }

    const response = await fetch(`${BACKEND_URL}/api/auth/session`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      credentials: "include",
    })

    if (!response.ok) {
      // Token might be expired or invalid
      if (response.status === 401 || response.status === 403) {
        removeToken()
      }
      return null
    }

    return response.json()
  },

  /**
   * Get the stored token
   */
  getToken,

  /**
   * Remove the stored token
   */
  removeToken,
}

export type AuthClient = typeof authClient
