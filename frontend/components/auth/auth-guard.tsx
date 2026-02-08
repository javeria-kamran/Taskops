"use client"

/**
 * Auth guard component to protect routes from unauthorized access
 */

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { authClient } from "@/lib/auth"

interface AuthGuardProps {
  children: React.ReactNode
  redirectTo?: string
  loadingComponent?: React.ReactNode
}

export function AuthGuard({
  children,
  redirectTo = "/signin",
  loadingComponent,
}: AuthGuardProps) {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check for token in localStorage
        const token = localStorage.getItem("auth_token")

        if (!token) {
          setIsAuthenticated(false)
          router.push(redirectTo)
          return
        }

        // Verify token with backend
        const session = await authClient.getSession()

        if (!session || !session.id) {
          setIsAuthenticated(false)
          localStorage.removeItem("auth_token")
          router.push(redirectTo)
          return
        }

        setIsAuthenticated(true)
      } catch (error) {
        console.error("Auth check failed:", error)
        setIsAuthenticated(false)
        localStorage.removeItem("auth_token")
        router.push(redirectTo)
      }
    }

    checkAuth()
  }, [router, redirectTo])

  // Loading state
  if (isAuthenticated === null) {
    return (
      loadingComponent || (
        <div className="flex min-h-screen items-center justify-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
            <p className="text-sm text-gray-600">Loading...</p>
          </div>
        </div>
      )
    )
  }

  // Not authenticated
  if (!isAuthenticated) {
    return null
  }

  // Authenticated - render children
  return <>{children}</>
}

/**
 * Hook to check if user is authenticated
 */
export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("auth_token")
        if (!token) {
          setIsAuthenticated(false)
          setIsLoading(false)
          return
        }

        const session = await authClient.getSession()
        if (session && session.id) {
          setIsAuthenticated(true)
          setUser(session)
        } else {
          setIsAuthenticated(false)
          localStorage.removeItem("auth_token")
        }
      } catch (error) {
        setIsAuthenticated(false)
        localStorage.removeItem("auth_token")
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const signout = async () => {
    try {
      await authClient.signout()
      localStorage.removeItem("auth_token")
      setIsAuthenticated(false)
      setUser(null)
    } catch (error) {
      console.error("Signout failed:", error)
    }
  }

  return { isAuthenticated, isLoading, user, signout }
}
