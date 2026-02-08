/**
 * Signup page for new user registration
 */

import Link from "next/link"
import { SignupForm } from "@/components/auth/signup-form"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

export const metadata = {
  title: "Sign Up - Taskops",
  description: "Create a new account to get started with Taskops",
}

export default function SignupPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F1F6FF] px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md ">
        <div className="text-center">
          <h1 className="mb-[0.8rem] text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700 bg-clip-text text-transparent">
            Taskops
          </h1>
         
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-zinc-800 font-semibold">Create your account</CardTitle>
            <CardDescription className="text-sm text-zinc-400">
              Sign up to start managing your tasks efficiently
            </CardDescription>
          </CardHeader>
          <CardContent>
            <SignupForm />

            <div className="mt-6 text-center text-sm text-gray-600">
              Already have an account?{" "}
              <Link
                href="/signin"
                className="font-medium text-[#1653DD] hover:text-[#1350BB]"
              >
                Sign in
              </Link>
            </div>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-gray-500 mt-[1rem]">
          By signing up, you agree to our{" "}
          <a href="/terms" className="underline hover:text-gray-700">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="/privacy" className="underline hover:text-gray-700">
            Privacy Policy
          </a>
        </p>
      </div>
    </div>
  )
}
