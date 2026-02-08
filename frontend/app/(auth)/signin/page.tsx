/**
 * Signin page for user authentication
 */

import Link from "next/link"
import { SigninForm } from "@/components/auth/signin-form"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

export const metadata = {
  title: "Sign In - Taskops",
  description: "Sign in to your Taskops account",
}

export default function SigninPage() {
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
            <CardTitle className="text-zinc-800 font-semibold">Welcome back</CardTitle>
            <CardDescription className="text-sm text-zinc-400">
              Sign in to your account to continue
            </CardDescription>
          </CardHeader>
          <CardContent>
            <SigninForm />

            <div className="mt-4 text-center text-sm text-gray-600">
              Don&apos;t have an account?{" "}
              <Link
                href="/signup"
                className="font-medium text-[#1653DD] hover:text-[#1350BB]"
              >
                Sign up
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
