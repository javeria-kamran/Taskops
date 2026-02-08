"use client"

/**
 * Signin form component for user login
 */

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { authClient } from "@/lib/auth"
import type { UserLogin } from "@/types/user"

interface SigninFormProps {
  onSuccess?: () => void
  redirectTo?: string
}

export function SigninForm({ onSuccess, redirectTo = "/tasks" }: SigninFormProps) {
  const router = useRouter()
  const [formData, setFormData] = useState<UserLogin>({
    email: "",
    password: "",
  })
  const [error, setError] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
    // Clear error when user starts typing
    if (error) setError("")
  }

  const validateForm = (): boolean => {
    if (!formData.email || !formData.password) {
      setError("Email and password are required")
      return false
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError("Please enter a valid email address")
      return false
    }

    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!validateForm()) {
      return
    }

    setIsLoading(true)

    try {
      const response = await authClient.signin(formData.email, formData.password)

      // Store token in localStorage (or use cookies via Better Auth)
      if (response.access_token) {
        localStorage.setItem("auth_token", response.access_token)
      }

      // Call success callback
      if (onSuccess) {
        onSuccess()
      }

      // Redirect to app
      router.push(redirectTo)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to sign in")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="email" className="text-sm font-medium text-gray-700">
          Email
        </label>
        <Input
          id="email"
          name="email"
          type="email"
          placeholder="you@example.com"
          value={formData.email}
          onChange={handleChange}
          disabled={isLoading}
          required
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="password" className="text-sm font-medium text-gray-700">
          Password
        </label>
        <Input
          id="password"
          name="password"
          type="password"
          placeholder="••••••••"
          value={formData.password}
          onChange={handleChange}
          disabled={isLoading}
          required
        />
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
          {error}
        </div>
      )}

      <Button type="submit" className="w-full bg-[#1653DD] text-white hover:bg-transparent hover:shadow-md border border-[#1653DD] hover:text-[#1653DD] font-medium" disabled={isLoading}>
        {isLoading ? "Signing in..." : "Sign in"}
      </Button>

     
    </form>
  )
}
