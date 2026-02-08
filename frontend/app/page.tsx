import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { MdArrowForward, MdChecklist, MdDoneAll, MdSmartToy } from 'react-icons/md';

export default function HomePage() {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-[#F1F6FF] px-4">
      {/* Auth buttons - Top right */}
      <div className="absolute top-6 right-6 flex items-center gap-3">
        <Link href="/signin">
          <Button variant="outline" className="border-[#1653DD] text-[#1653DD] hover:shadow-md hover:font-semibold !bg-transparent">
            Sign In
          </Button>
        </Link>
        <Link href="/signup">
          <Button className="bg-[#1653DD] text-white hover:bg-transparent hover:shadow-md border border-[#1653DD] hover:text-[#1653DD]">
            Sign Up
          </Button>
        </Link>
      </div>

      <div className="w-full max-w-4xl text-center">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700 bg-clip-text text-transparent">
          Get Started With Taskops
        </h1>

        <Card
          className="mt-4 mx-auto max-w-2xl"
          style={{
            background: 'linear-gradient(#7DA4FF, #D7E3FF)',
            boxShadow: '0px 8px 24px #2945800D',
          }}
        >
          <CardHeader>
            <CardTitle className="text-xl text-center">
              Manage your tasks efficiently with AI-powered assistance
            </CardTitle>
          </CardHeader>

          <CardContent>
            <div className="mt-6 grid gap-6 sm:grid-cols-3 text-left">
              {/* Feature 1 */}
              <div className="space-y-1">
                <div className="flex items-center gap-1">
                  <MdChecklist className="text-blue-700 text-lg" />
                  <h3 className="font-semibold text-gray-900">Task Management</h3>
                </div>
                <p className="text-sm text-gray-600">
                  Create, organize, and track your tasks with ease
                </p>
              </div>

              {/* Feature 2 */}
              <div className="space-y-1">
                <div className="flex items-center gap-1">
                  <MdDoneAll className="text-green-600 text-lg" />
                  <h3 className="font-semibold text-gray-900">Smart Completion</h3>
                </div>
                <p className="text-sm text-gray-600">
                  Mark tasks complete and track your progress
                </p>
              </div>


              {/* Feature 3 */}
              <div className="space-y-1">
                <div className="flex items-center gap-1">
                  <MdSmartToy className="text-purple-600 text-xl" />
                  <h3 className="font-semibold text-gray-900">AI Assistant</h3>
                </div>
                <p className="text-sm text-gray-600">
                  Manage tasks with AI-chatbot
                </p>
              </div>

            </div>

            {/* Center buttons */}
            <div className="mt-[3rem] flex justify-center gap-4">
              <Link href="/signup">
                <Button className="bg-[#1653DD] !w-[12rem] text-white hover:bg-[#1350BB]">
                  Get Started
                </Button>
              </Link>
              <Link href="/signin">
                <Button variant="ghost" className="text-[#1653DD] hover:bg-transparent flex items-center gap-1">
                  Sign In <MdArrowForward />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        <p className="mt-4 text-sm text-gray-500">
          Phase II: Web Application with Authentication
        </p>
      </div>
    </div>
  )
}
