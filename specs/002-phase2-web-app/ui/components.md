# UI Components Specification

## Overview

This document specifies all reusable UI components for the Phase II web application. Components follow Next.js 16+ App Router patterns with a mix of Server and Client Components.

**Design System**: Tailwind CSS
**Component Library**: Custom (no third-party UI libraries for Basic Level)
**Accessibility**: WCAG 2.1 AA compliance

## Component Architecture

### Server vs Client Components

**Default**: Server Components (better performance, smaller bundle)
**Use Client Components when**:
- Need event handlers (onClick, onChange)
- Need state (useState, useReducer)
- Need effects (useEffect)
- Need browser APIs

## Base UI Components

### Button Component

**File**: `components/ui/button.tsx`
**Type**: Server Component

```typescript
import { ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        // Base styles
        'inline-flex items-center justify-center rounded-md font-medium transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',

        // Variants
        {
          'bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-600': variant === 'primary',
          'bg-gray-200 text-gray-900 hover:bg-gray-300 focus-visible:ring-gray-400': variant === 'secondary',
          'bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-600': variant === 'danger',
          'hover:bg-gray-100 focus-visible:ring-gray-400': variant === 'ghost',
        },

        // Sizes
        {
          'h-8 px-3 text-sm': size === 'sm',
          'h-10 px-4 text-base': size === 'md',
          'h-12 px-6 text-lg': size === 'lg',
        },

        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}
```

**Usage**:
```tsx
<Button variant="primary" onClick={handleSubmit}>Save Task</Button>
<Button variant="danger" size="sm">Delete</Button>
```

---

### Input Component

**File**: `components/ui/input.tsx`
**Type**: Server Component

```typescript
import { InputHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string
}

export function Input({ error, className, ...props }: InputProps) {
  return (
    <div className="w-full">
      <input
        className={cn(
          'w-full rounded-md border px-3 py-2',
          'focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent',
          'disabled:cursor-not-allowed disabled:opacity-50',
          error ? 'border-red-500' : 'border-gray-300',
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
```

**Usage**:
```tsx
<Input
  type="text"
  placeholder="Task title"
  error={errors.title}
/>
```

---

### Textarea Component

**File**: `components/ui/textarea.tsx`
**Type**: Server Component

```typescript
import { TextareaHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string
}

export function Textarea({ error, className, ...props }: TextareaProps) {
  return (
    <div className="w-full">
      <textarea
        className={cn(
          'w-full rounded-md border px-3 py-2 min-h-[100px]',
          'focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent',
          'disabled:cursor-not-allowed disabled:opacity-50',
          error ? 'border-red-500' : 'border-gray-300',
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
```

---

### Card Component

**File**: `components/ui/card.tsx`
**Type**: Server Component

```typescript
import { HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'rounded-lg border border-gray-200 bg-white shadow-sm',
        className
      )}
      {...props}
    />
  )
}

export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('p-6 border-b border-gray-200', className)} {...props} />
}

export function CardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('p-6', className)} {...props} />
}
```

**Usage**:
```tsx
<Card>
  <CardHeader>
    <h2>My Tasks</h2>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
</Card>
```

---

### Checkbox Component

**File**: `components/ui/checkbox.tsx`
**Type**: Client Component (requires state)

```typescript
'use client'

import { InputHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
}

export function Checkbox({ label, className, id, ...props }: CheckboxProps) {
  const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`

  return (
    <div className="flex items-center">
      <input
        type="checkbox"
        id={checkboxId}
        className={cn(
          'h-5 w-5 rounded border-gray-300 text-blue-600',
          'focus:ring-2 focus:ring-blue-600 focus:ring-offset-2',
          'cursor-pointer',
          className
        )}
        {...props}
      />
      {label && (
        <label
          htmlFor={checkboxId}
          className="ml-2 text-sm text-gray-700 cursor-pointer"
        >
          {label}
        </label>
      )}
    </div>
  )
}
```

---

### Loading Spinner

**File**: `components/ui/loading.tsx`
**Type**: Server Component

```typescript
import { cn } from '@/lib/utils'

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Loading({ size = 'md', className }: LoadingProps) {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-3',
    lg: 'h-12 w-12 border-4',
  }

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-blue-600 border-t-transparent',
        sizeClasses[size],
        className
      )}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  )
}
```

---

### Modal/Dialog Component

**File**: `components/ui/dialog.tsx`
**Type**: Client Component (requires state and portal)

```typescript
'use client'

import { ReactNode, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { cn } from '@/lib/utils'

interface DialogProps {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
  footer?: ReactNode
}

export function Dialog({ open, onClose, title, children, footer }: DialogProps) {
  // Close on Escape key
  useEffect(() => {
    if (!open) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [open, onClose])

  if (!open) return null

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Dialog */}
      <div
        className={cn(
          'relative bg-white rounded-lg shadow-xl',
          'w-full max-w-md mx-4',
          'max-h-[90vh] overflow-y-auto'
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 id="dialog-title" className="text-xl font-semibold">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close dialog"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">{children}</div>

        {/* Footer */}
        {footer && (
          <div className="flex items-center justify-end gap-3 p-6 border-t">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body
  )
}
```

---

## Task Components

### TaskList Component

**File**: `components/tasks/task-list.tsx`
**Type**: Server Component

```typescript
import { TaskItem } from './task-item'
import { Task } from '@/types/task'

interface TaskListProps {
  tasks: Task[]
}

export function TaskList({ tasks }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No tasks yet</p>
        <p className="text-sm mt-2">Create your first task to get started!</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem key={task.id} task={task} />
      ))}
    </div>
  )
}
```

---

### TaskItem Component

**File**: `components/tasks/task-item.tsx`
**Type**: Client Component (interactive)

```typescript
'use client'

import { useState } from 'react'
import { Task } from '@/types/task'
import { Checkbox } from '@/components/ui/checkbox'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { useRouter } from 'next/navigation'

interface TaskItemProps {
  task: Task
}

export function TaskItem({ task }: TaskItemProps) {
  const router = useRouter()
  const [isToggling, setIsToggling] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleToggle = async () => {
    setIsToggling(true)
    try {
      await api.toggleComplete(task.id)
      router.refresh() // Refresh Server Component
    } catch (error) {
      console.error('Failed to toggle task:', error)
    } finally {
      setIsToggling(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Delete this task? This cannot be undone.')) return

    setIsDeleting(true)
    try {
      await api.deleteTask(task.id)
      router.refresh()
    } catch (error) {
      console.error('Failed to delete task:', error)
      setIsDeleting(false)
    }
  }

  return (
    <div className="group p-4 border rounded-lg hover:bg-gray-50 transition-colors">
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <Checkbox
          checked={task.completed}
          onChange={handleToggle}
          disabled={isToggling}
          className="mt-0.5"
        />

        {/* Task content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-base font-medium ${
              task.completed ? 'line-through text-gray-500' : 'text-gray-900'
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p className="mt-1 text-sm text-gray-600">{task.description}</p>
          )}
          <p className="mt-2 text-xs text-gray-400">
            Created {new Date(task.createdAt).toLocaleDateString()}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push(`/tasks/${task.id}/edit`)}
          >
            Edit
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </div>
    </div>
  )
}
```

---

### TaskForm Component

**File**: `components/tasks/task-form.tsx`
**Type**: Client Component (form state)

```typescript
'use client'

import { useState, FormEvent } from 'react'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { useRouter } from 'next/navigation'

interface TaskFormProps {
  mode: 'create' | 'edit'
  initialData?: {
    title: string
    description: string
  }
  taskId?: number
}

export function TaskForm({ mode, initialData, taskId }: TaskFormProps) {
  const router = useRouter()
  const [title, setTitle] = useState(initialData?.title || '')
  const [description, setDescription] = useState(initialData?.description || '')
  const [errors, setErrors] = useState<{ title?: string; description?: string }>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validate = () => {
    const newErrors: typeof errors = {}

    if (!title.trim()) {
      newErrors.title = 'Title is required'
    } else if (title.length > 200) {
      newErrors.title = 'Title must be 200 characters or less'
    }

    if (description.length > 1000) {
      newErrors.description = 'Description must be 1000 characters or less'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!validate()) return

    setIsSubmitting(true)
    try {
      const data = { title: title.trim(), description: description.trim() }

      if (mode === 'create') {
        await api.createTask(data)
        setTitle('')
        setDescription('')
      } else if (mode === 'edit' && taskId) {
        await api.updateTask(taskId, data)
      }

      router.refresh()
      if (mode === 'edit') router.push('/tasks')
    } catch (error) {
      console.error('Failed to save task:', error)
      setErrors({ title: 'Failed to save task. Please try again.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title *
        </label>
        <Input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task title"
          error={errors.title}
          disabled={isSubmitting}
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description (optional)
        </label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more details..."
          error={errors.description}
          disabled={isSubmitting}
        />
      </div>

      <div className="flex gap-2">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Saving...' : mode === 'create' ? 'Add Task' : 'Save Changes'}
        </Button>
        {mode === 'edit' && (
          <Button type="button" variant="secondary" onClick={() => router.push('/tasks')}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  )
}
```

---

## Authentication Components

### SignupForm Component

**File**: `components/auth/signup-form.tsx`
**Type**: Client Component

```typescript
'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { auth } from '@/lib/auth'
import Link from 'next/link'

export function SignupForm() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [name, setName] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validate = () => {
    const newErrors: Record<string, string> = {}

    if (!email) newErrors.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) newErrors.email = 'Invalid email format'

    if (!password) newErrors.password = 'Password is required'
    else if (password.length < 8) newErrors.password = 'Password must be at least 8 characters'

    if (password !== confirmPassword) newErrors.confirmPassword = 'Passwords do not match'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setIsSubmitting(true)
    try {
      await auth.signup({ email, password, name: name || undefined })
      router.push('/tasks')
    } catch (error: any) {
      setErrors({ email: error.message || 'Failed to create account' })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">Email</label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
          autoComplete="email"
        />
      </div>

      <div>
        <label htmlFor="name" className="block text-sm font-medium mb-1">Name (optional)</label>
        <Input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoComplete="name"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium mb-1">Password</label>
        <Input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
          autoComplete="new-password"
        />
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1">
          Confirm Password
        </label>
        <Input
          id="confirmPassword"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          error={errors.confirmPassword}
          autoComplete="new-password"
        />
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? 'Creating account...' : 'Sign Up'}
      </Button>

      <p className="text-center text-sm text-gray-600">
        Already have an account?{' '}
        <Link href="/signin" className="text-blue-600 hover:underline">
          Sign in
        </Link>
      </p>
    </form>
  )
}
```

---

### SigninForm Component

**File**: `components/auth/signin-form.tsx`
**Type**: Client Component (similar to SignupForm, simpler)

---

### Nav Component

**File**: `components/layout/nav.tsx`
**Type**: Server Component with Client dropdown

```typescript
import { auth } from '@/lib/auth'
import { SignoutButton } from './signout-button'
import Link from 'next/link'

export async function Nav() {
  const session = await auth.getSession()

  if (!session) return null

  return (
    <nav className="border-b bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/tasks" className="text-xl font-bold text-blue-600">
            Naz Todo
          </Link>

          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{session.user.email}</span>
            <SignoutButton />
          </div>
        </div>
      </div>
    </nav>
  )
}
```

---

## Component Guidelines

### Naming Conventions
- PascalCase for component names
- Descriptive names (TaskForm, not Form)
- File names match component names

### File Organization
```
components/
├── ui/               # Base reusable components
│   ├── button.tsx
│   ├── input.tsx
│   ├── checkbox.tsx
│   └── dialog.tsx
├── tasks/            # Task-specific components
│   ├── task-list.tsx
│   ├── task-item.tsx
│   └── task-form.tsx
├── auth/             # Auth components
│   ├── signup-form.tsx
│   └── signin-form.tsx
└── layout/           # Layout components
    └── nav.tsx
```

### Accessibility
- All interactive elements keyboard accessible
- Proper ARIA labels and roles
- Color contrast meets WCAG AA
- Form inputs have associated labels
- Error messages announced to screen readers

### Performance
- Use Server Components by default
- Only mark as Client Component when needed
- Lazy load heavy components
- Optimize images with next/image

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial UI components specification |
