"use client"

/**
 * Protected app layout with authentication guard and navigation
 */

import { AuthGuard, useAuth } from "@/components/auth/auth-guard"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"

interface AppLayoutProps {
  children: React.ReactNode
}

function AppLayoutContent({ children }: AppLayoutProps) {
  const { user, signout } = useAuth()
  const router = useRouter()

  const handleSignout = async () => {
    await signout()
    router.push("/signin")
  }

  return (
    <div className="min-h-screen bg-[#F1F6FF]">
      {/* Navigation Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Taskops</h1>
            </div>

            <nav className="flex items-center space-x-4">
              <a
                href="/tasks"
                className="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                All Tasks
              </a>

              {user && (
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-gray-600">
                    {user.name || user.email}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-[#1653DD] text-[#1653DD] hover:bg-[#F1F6FF]"
                    onClick={handleSignout}
                  >
                    Sign out
                  </Button>
                </div>
              )}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            &copy; {new Date().getFullYear()} Taskops. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default function AppLayout({ children }: AppLayoutProps) {
  return (
    <AuthGuard>
      <AppLayoutContent>{children}</AppLayoutContent>
    </AuthGuard>
  )
}
