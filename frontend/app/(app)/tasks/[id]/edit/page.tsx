"use client"

/**
 * Task edit page
 */

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { TaskForm } from "@/components/tasks/task-form"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { tasksApi } from "@/lib/api"
import type { Task } from "@/types/task"

export default function EditTaskPage() {
  const params = useParams()
  const router = useRouter()
  const taskId = params.id as string

  const [task, setTask] = useState<Task | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>("")

  useEffect(() => {
    loadTask()
  }, [taskId])

  const loadTask = async () => {
    setIsLoading(true)
    setError("")

    try {
      const fetchedTask = await tasksApi.getById(taskId)
      setTask(fetchedTask)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load task")
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuccess = () => {
    router.push("/tasks")
  }

  const handleCancel = () => {
    router.push("/tasks")
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <Card>
          <CardContent className="p-12">
            <div className="flex flex-col items-center justify-center">
              <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
              <p className="mt-4 text-sm text-gray-600">Loading task...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Edit Task</h1>
          <p className="mt-2 text-sm text-gray-600">
            Modify your task details
          </p>
        </div>

        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <svg
                className="h-5 w-5 text-red-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-sm font-medium text-red-800">{error}</p>
            </div>
            <div className="mt-4 flex gap-2">
              <button
                onClick={loadTask}
                className="rounded-md bg-white px-4 py-2 text-sm font-medium text-red-900 shadow-sm hover:bg-red-50"
              >
                Try Again
              </button>
              <button
                onClick={handleCancel}
                className="rounded-md bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
              >
                Go Back
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!task) {
    return null
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Edit Task</h1>
        <p className="mt-2 text-sm text-gray-600">
          Modify your task details
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Task Details</CardTitle>
          <CardDescription>
            Update the task information below
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TaskForm
            task={task}
            onSuccess={handleSuccess}
            onCancel={handleCancel}
          />
        </CardContent>
      </Card>
    </div>
  )
}
