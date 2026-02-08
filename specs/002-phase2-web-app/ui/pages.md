# UI Pages Specification

## Overview

This document specifies all pages (routes) for the Phase II web application using Next.js 16+ App Router.

**Routing**: File-system based (App Router)
**Rendering**: Mix of Server and Client Components
**Data Fetching**: Server Components for initial data, Client Components for mutations

## Route Structure

```
app/
├── page.tsx                    # Landing page (/)
├── layout.tsx                  # Root layout
├── (auth)/                     # Auth group (shared layout)
│   ├── layout.tsx             # Auth layout
│   ├── signup/
│   │   └── page.tsx           # Signup page (/signup)
│   └── signin/
│       └── page.tsx           # Signin page (/signin)
└── (app)/                      # Protected app group
    ├── layout.tsx             # App layout with nav
    └── tasks/
        ├── page.tsx           # Task list page (/tasks)
        ├── new/
        │   └── page.tsx       # New task page (/tasks/new)
        └── [id]/
            └── edit/
                └── page.tsx   # Edit task page (/tasks/[id]/edit)
```

## Landing Page

**Route**: `/`
**File**: `app/page.tsx`
**Type**: Server Component
**Auth**: Public

### Purpose
- Welcome users to the application
- Provide links to signup/signin
- If user is already authenticated, redirect to /tasks

### Layout
```
┌─────────────────────────────────────────┐
│              [Logo]                     │
│          Naz Todo                       │
│                                         │
│   Simple task management for everyone  │
│                                         │
│     [Sign Up] button   [Sign In] link  │
│                                         │
└─────────────────────────────────────────┘
```

### Implementation
```typescript
// app/page.tsx
import { redirect } from 'next/navigation'
import { auth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default async function HomePage() {
  const session = await auth.getSession()

  // Redirect if already authenticated
  if (session) {
    redirect('/tasks')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full text-center space-y-8 p-8">
        <div>
          <h1 className="text-4xl font-bold text-blue-600 mb-2">Naz Todo</h1>
          <p className="text-gray-600">Simple task management for everyone</p>
        </div>

        <div className="space-y-4">
          <Link href="/signup" className="block">
            <Button className="w-full" size="lg">
              Get Started
            </Button>
          </Link>

          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link href="/signin" className="text-blue-600 hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
```

---

## Signup Page

**Route**: `/signup`
**File**: `app/(auth)/signup/page.tsx`
**Type**: Server Component (with Client Component form)
**Auth**: Public (redirects if authenticated)

### Purpose
- Allow new users to create an account
- Validate email and password
- Redirect to /tasks after successful signup

### Layout
```
┌─────────────────────────────────────────┐
│         [Logo] Naz Todo                 │
│                                         │
│      Create Your Account                │
│                                         │
│  Email                                  │
│  [_________________________________]    │
│                                         │
│  Name (optional)                        │
│  [_________________________________]    │
│                                         │
│  Password                               │
│  [_________________________________]    │
│                                         │
│  Confirm Password                       │
│  [_________________________________]    │
│                                         │
│       [Sign Up] button                  │
│                                         │
│  Already have an account? Sign in       │
│                                         │
└─────────────────────────────────────────┘
```

### Implementation
```typescript
// app/(auth)/signup/page.tsx
import { redirect } from 'next/navigation'
import { auth } from '@/lib/auth'
import { SignupForm } from '@/components/auth/signup-form'
import Link from 'next/link'

export default async function SignupPage() {
  const session = await auth.getSession()

  if (session) {
    redirect('/tasks')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Link href="/" className="text-2xl font-bold text-blue-600">
            Naz Todo
          </Link>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Create your account
          </h2>
        </div>

        <div className="bg-white py-8 px-6 shadow rounded-lg">
          <SignupForm />
        </div>
      </div>
    </div>
  )
}
```

---

## Signin Page

**Route**: `/signin`
**File**: `app/(auth)/signin/page.tsx`
**Type**: Server Component (with Client Component form)
**Auth**: Public (redirects if authenticated)

### Purpose
- Allow existing users to sign in
- Validate credentials
- Redirect to /tasks after successful signin

### Layout
```
┌─────────────────────────────────────────┐
│         [Logo] Naz Todo                 │
│                                         │
│         Welcome Back                    │
│                                         │
│  Email                                  │
│  [_________________________________]    │
│                                         │
│  Password                               │
│  [_________________________________]    │
│                                         │
│  [ ] Remember me                       │
│                                         │
│       [Sign In] button                  │
│                                         │
│  Don't have an account? Sign up         │
│                                         │
└─────────────────────────────────────────┘
```

### Implementation
```typescript
// app/(auth)/signin/page.tsx
import { redirect } from 'next/navigation'
import { auth } from '@/lib/auth'
import { SigninForm } from '@/components/auth/signin-form'
import Link from 'next/link'

export default async function SigninPage() {
  const session = await auth.getSession()

  if (session) {
    redirect('/tasks')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Link href="/" className="text-2xl font-bold text-blue-600">
            Naz Todo
          </Link>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Welcome back
          </h2>
        </div>

        <div className="bg-white py-8 px-6 shadow rounded-lg">
          <SigninForm />
        </div>
      </div>
    </div>
  )
}
```

---

## Task List Page (Main App)

**Route**: `/tasks`
**File**: `app/(app)/tasks/page.tsx`
**Type**: Server Component (fetches initial data)
**Auth**: Required (redirects to /signin if not authenticated)

### Purpose
- Display all tasks for the authenticated user
- Show task creation form
- Allow quick actions (complete, edit, delete)

### Layout
```
┌─────────────────────────────────────────────────┐
│ [Logo] Naz Todo           user@email.com [▼]   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ Add New Task                            │   │
│  │ Title: [__________________________]     │   │
│  │ Description:                            │   │
│  │ [_________________________________]     │   │
│  │              [Add Task] button          │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ ☐ Buy groceries              [Edit][Del]│   │
│  │   Milk, eggs, bread                     │   │
│  │   Created: 2 hours ago                  │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ ☑ Finish homework            [Edit][Del]│   │
│  │   Math pages 10-15                      │   │
│  │   Created: 1 day ago                    │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Implementation
```typescript
// app/(app)/tasks/page.tsx
import { redirect } from 'next/navigation'
import { auth } from '@/lib/auth'
import { api } from '@/lib/api'
import { TaskList } from '@/components/tasks/task-list'
import { TaskForm } from '@/components/tasks/task-form'
import { Card, CardHeader, CardContent } from '@/components/ui/card'

export default async function TasksPage() {
  const session = await auth.getSession()

  if (!session) {
    redirect('/signin')
  }

  // Fetch tasks server-side
  const tasks = await api.getTasks()

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-8">My Tasks</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Task creation form */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold">Add New Task</h2>
            </CardHeader>
            <CardContent>
              <TaskForm mode="create" />
            </CardContent>
          </Card>
        </div>

        {/* Task list */}
        <div className="lg:col-span-2">
          <TaskList tasks={tasks} />
        </div>
      </div>
    </div>
  )
}

// Opt out of caching for this page (always fresh data)
export const dynamic = 'force-dynamic'
```

---

## Edit Task Page

**Route**: `/tasks/[id]/edit`
**File**: `app/(app)/tasks/[id]/edit/page.tsx`
**Type**: Server Component (fetches task data)
**Auth**: Required

### Purpose
- Edit an existing task's title and description
- Pre-fill form with current task data
- Redirect to /tasks after successful update

### Layout
```
┌─────────────────────────────────────────────────┐
│ [Logo] Naz Todo           user@email.com [▼]   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ← Back to Tasks                                │
│                                                 │
│  Edit Task                                      │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ Title *                                  │   │
│  │ [Buy groceries___________________]      │   │
│  │                                          │   │
│  │ Description                              │   │
│  │ [Milk, eggs, bread_______________]      │   │
│  │ [________________________________]      │   │
│  │                                          │   │
│  │ [Save Changes] [Cancel] buttons         │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Implementation
```typescript
// app/(app)/tasks/[id]/edit/page.tsx
import { redirect, notFound } from 'next/navigation'
import { auth } from '@/lib/auth'
import { api } from '@/lib/api'
import { TaskForm } from '@/components/tasks/task-form'
import { Card, CardHeader, CardContent } from '@/components/ui/card'
import Link from 'next/link'

interface EditTaskPageProps {
  params: { id: string }
}

export default async function EditTaskPage({ params }: EditTaskPageProps) {
  const session = await auth.getSession()

  if (!session) {
    redirect('/signin')
  }

  // Fetch task server-side
  const taskId = parseInt(params.id)
  if (isNaN(taskId)) {
    notFound()
  }

  const task = await api.getTask(taskId)

  if (!task) {
    notFound()
  }

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <Link
        href="/tasks"
        className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-6"
      >
        ← Back to Tasks
      </Link>

      <h1 className="text-3xl font-bold mb-8">Edit Task</h1>

      <Card>
        <CardContent className="pt-6">
          <TaskForm
            mode="edit"
            taskId={task.id}
            initialData={{
              title: task.title,
              description: task.description || '',
            }}
          />
        </CardContent>
      </Card>
    </div>
  )
}

export const dynamic = 'force-dynamic'
```

---

## Layouts

### Root Layout

**File**: `app/layout.tsx`
**Type**: Server Component

```typescript
// app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Naz Todo - Simple Task Management',
  description: 'Manage your tasks efficiently',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

---

### App Layout (Protected Routes)

**File**: `app/(app)/layout.tsx`
**Type**: Server Component

```typescript
// app/(app)/layout.tsx
import { redirect } from 'next/navigation'
import { auth } from '@/lib/auth'
import { Nav } from '@/components/layout/nav'

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await auth.getSession()

  if (!session) {
    redirect('/signin')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <main>{children}</main>
    </div>
  )
}
```

---

### Auth Layout

**File**: `app/(auth)/layout.tsx`
**Type**: Server Component

```typescript
// app/(auth)/layout.tsx
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <div className="min-h-screen bg-gray-50">{children}</div>
}
```

---

## Route Protection

### Middleware Approach (Alternative)

**File**: `middleware.ts`

```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { auth } from '@/lib/auth'

export async function middleware(request: NextRequest) {
  const session = await auth.getSession()

  // Protected routes
  if (request.nextUrl.pathname.startsWith('/tasks')) {
    if (!session) {
      return NextResponse.redirect(new URL('/signin', request.url))
    }
  }

  // Auth routes (redirect if already signed in)
  if (
    request.nextUrl.pathname.startsWith('/signin') ||
    request.nextUrl.pathname.startsWith('/signup')
  ) {
    if (session) {
      return NextResponse.redirect(new URL('/tasks', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

---

## Loading States

### Loading UI

**File**: `app/(app)/tasks/loading.tsx`

```typescript
// app/(app)/tasks/loading.tsx
import { Loading } from '@/components/ui/loading'

export default function TasksLoading() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loading size="lg" />
          <p className="mt-4 text-gray-600">Loading tasks...</p>
        </div>
      </div>
    </div>
  )
}
```

---

## Error States

### Error UI

**File**: `app/(app)/tasks/error.tsx`

```typescript
'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function TasksError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Tasks page error:', error)
  }, [error])

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-red-600 mb-4">
          Something went wrong!
        </h2>
        <p className="text-gray-600 mb-6">
          Failed to load tasks. Please try again.
        </p>
        <Button onClick={reset}>Try again</Button>
      </div>
    </div>
  )
}
```

---

## Not Found Page

**File**: `app/not-found.tsx`

```typescript
// app/not-found.tsx
import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-700 mb-6">
          Page not found
        </h2>
        <p className="text-gray-600 mb-8">
          The page you're looking for doesn't exist.
        </p>
        <Link href="/tasks">
          <Button>Go to Tasks</Button>
        </Link>
      </div>
    </div>
  )
}
```

---

## Responsive Design

### Breakpoints (Tailwind)
- **Mobile**: < 640px (sm)
- **Tablet**: 640px - 1024px (md-lg)
- **Desktop**: > 1024px (xl)

### Mobile Adaptations

**Task List Page**:
- Stack task form above task list (not side-by-side)
- Full-width cards
- Smaller text and padding

**Task Item**:
- Hide edit/delete buttons by default (always visible on mobile)
- Show on tap/focus

**Forms**:
- Full-width inputs
- Larger touch targets (min 44x44px)

---

## SEO & Metadata

### Per-Page Metadata

```typescript
// app/(app)/tasks/page.tsx
export const metadata = {
  title: 'My Tasks | Naz Todo',
  description: 'Manage your tasks',
}

// app/(auth)/signup/page.tsx
export const metadata = {
  title: 'Sign Up | Naz Todo',
  description: 'Create a free account',
}
```

---

## Performance Optimization

### Data Fetching Strategy
- Use Server Components for initial data (faster first load)
- Use Client Components for mutations (optimistic updates)
- Cache API responses when appropriate

### Code Splitting
- Automatic with Next.js App Router
- Lazy load heavy components (e.g., rich text editor in future)

### Image Optimization
- Use next/image for all images
- Proper sizing and lazy loading

---

## Accessibility

### Keyboard Navigation
- All interactive elements focusable
- Tab order logical (top to bottom, left to right)
- Escape key closes modals

### Screen Readers
- Proper heading hierarchy (h1 → h2 → h3)
- ARIA labels for icon buttons
- Live regions for dynamic updates

### Focus Management
- Visible focus indicators
- Focus trapped in modals
- Focus returned after modal close

---

## Testing Strategy

### Page-Level Tests

**Tasks Page**:
- Renders task list correctly
- Shows empty state when no tasks
- Creates task successfully
- Redirects to signin when not authenticated

**Signin Page**:
- Form validation works
- Successful signin redirects to /tasks
- Error messages display correctly
- Redirects to /tasks if already signed in

### E2E Tests (Playwright)

```typescript
// tests/e2e/tasks.spec.ts
import { test, expect } from '@playwright/test'

test('complete task flow', async ({ page }) => {
  // Sign in
  await page.goto('/signin')
  await page.fill('input[type="email"]', 'test@example.com')
  await page.fill('input[type="password"]', 'password123')
  await page.click('button[type="submit"]')

  // Verify redirected to tasks page
  await expect(page).toHaveURL('/tasks')

  // Create task
  await page.fill('input[name="title"]', 'Test task')
  await page.click('button:has-text("Add Task")')

  // Verify task appears
  await expect(page.locator('text=Test task')).toBeVisible()

  // Toggle completion
  await page.click('input[type="checkbox"]')
  await expect(page.locator('text=Test task')).toHaveClass(/line-through/)

  // Delete task
  await page.click('button:has-text("Delete")')
  await page.click('button:has-text("Confirm")')
  await expect(page.locator('text=Test task')).not.toBeVisible()
})
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial UI pages specification |
