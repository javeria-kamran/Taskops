"use client"

/**
 * Signup form component for new user registration
 */

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { authClient } from "@/lib/auth"
import type { UserCreate } from "@/types/user"

interface SignupFormProps {
  onSuccess?: () => void
  redirectTo?: string
}

export function SignupForm({ onSuccess, redirectTo = "/tasks" }: SignupFormProps) {
  const router = useRouter()
  const [formData, setFormData] = useState<UserCreate>({
    email: "",
    password: "",
    name: "",
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

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long")
      return false
    }

    if (!/[A-Z]/.test(formData.password)) {
      setError("Password must contain at least one uppercase letter")
      return false
    }

    if (!/[a-z]/.test(formData.password)) {
      setError("Password must contain at least one lowercase letter")
      return false
    }

    if (!/[0-9]/.test(formData.password)) {
      setError("Password must contain at least one digit")
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
      const response = await authClient.signup(
        formData.email,
        formData.password,
        formData.name || undefined
      )

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
      setError(err instanceof Error ? err.message : "Failed to sign up")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="name" className="text-sm font-medium text-gray-700">
          Name (optional)
        </label>
        <Input
          id="name"
          name="name"
          type="text"
          placeholder="John Doe"
          value={formData.name}
          onChange={handleChange}
          disabled={isLoading}
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="email" className="text-sm font-medium text-gray-700">
          Email <span className="text-red-500">*</span>
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
          Password <span className="text-red-500">*</span>
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
        <p className="text-xs text-gray-500">
          Must be at least 8 characters with uppercase, lowercase, and digit
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
          {error}
        </div>
      )}

      <Button type="submit" className="w-full bg-[#1653DD] text-white hover:bg-transparent hover:shadow-md border border-[#1653DD] hover:text-[#1653DD] font-medium" disabled={isLoading}>
        {isLoading ? "Creating account..." : "Sign up"}
      </Button>
    </form>
  )
}
