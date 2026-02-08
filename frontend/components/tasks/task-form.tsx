"use client"

/**
 * Task form component for creating and editing tasks
 */

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { tasksApi } from "@/lib/api"
import type { TaskCreate, Task } from "@/types/task"

interface TaskFormProps {
  task?: Task
  onSuccess?: (task: Task) => void
  onCancel?: () => void
}

export function TaskForm({ task, onSuccess, onCancel }: TaskFormProps) {
  const router = useRouter()
  const isEditing = !!task

  const [formData, setFormData] = useState<TaskCreate>({
    title: task?.title || "",
    description: task?.description || "",
  })
  const [error, setError] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
    // Clear error when user starts typing
    if (error) setError("")
  }

  const validateForm = (): boolean => {
    if (!formData.title || !formData.title.trim()) {
      setError("Title is required")
      return false
    }

    if (formData.title.length > 200) {
      setError("Title cannot exceed 200 characters")
      return false
    }

    if (formData.description && formData.description.length > 1000) {
      setError("Description cannot exceed 1000 characters")
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
      const taskData: TaskCreate = {
        title: formData.title.trim(),
        description: formData.description?.trim() || undefined,
      }

      let result: Task

      if (isEditing && task) {
        // Update existing task
        result = await tasksApi.update(task.id, taskData)
      } else {
        // Create new task
        result = await tasksApi.create(taskData)
      }

      // Call success callback or redirect
      if (onSuccess) {
        onSuccess(result)
      } else {
        router.push("/tasks")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save task")
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancelClick = () => {
    if (onCancel) {
      onCancel()
    } else {
      router.push("/tasks")
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <label htmlFor="title" className="text-sm font-medium text-gray-700">
          Title <span className="text-red-500">*</span>
        </label>
        <Input
          id="title"
          name="title"
          type="text"
          placeholder="Enter task title..."
          value={formData.title}
          onChange={handleChange}
          disabled={isLoading}
          required
          maxLength={200}
        />
        <p className="text-xs text-gray-500">
          {formData.title.length}/200 characters
        </p>
      </div>

      <div className="space-y-2">
        <label
          htmlFor="description"
          className="text-sm font-medium text-gray-700"
        >
          Description (optional)
        </label>
        <textarea
          id="description"
          name="description"
          placeholder="Add more details about this task..."
          value={formData.description}
          onChange={handleChange}
          disabled={isLoading}
          maxLength={1000}
          rows={4}
          className="flex w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1653DD] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        />
        <p className="text-xs text-gray-500">
          {formData.description?.length || 0}/1000 characters
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
          {error}
        </div>
      )}

      <div className="flex gap-3">
        <Button type="submit" className="bg-[#1653DD] text-white hover:bg-[#1350BB]" disabled={isLoading}>
          {isLoading
            ? isEditing
              ? "Updating..."
              : "Creating..."
            : isEditing
            ? "Update Task"
            : "Create Task"}
        </Button>
        <Button
          type="button"
          variant="outline"
          className="border-[#1653DD] text-[#1653DD]"
          onClick={handleCancelClick}
          disabled={isLoading}
        >
          Cancel
        </Button>
      </div>
    </form>
  )
}
