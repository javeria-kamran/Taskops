"use client"

/**
 * Task item component for displaying individual tasks
 */

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { tasksApi } from "@/lib/api"
import { formatDate } from "@/lib/utils"
import type { Task } from "@/types/task"

interface TaskItemProps {
  task: Task
  onUpdate?: (task: Task) => void
  onDelete?: (taskId: string) => void
}

export function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const router = useRouter()
  const [isToggling, setIsToggling] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleToggleComplete = async () => {
    setIsToggling(true)
    try {
      const updatedTask = await tasksApi.toggleComplete(task.id, !task.completed)
      if (onUpdate) {
        onUpdate(updatedTask)
      }
    } catch (error) {
      console.error("Failed to toggle task:", error)
    } finally {
      setIsToggling(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this task?")) {
      return
    }

    setIsDeleting(true)
    try {
      await tasksApi.delete(task.id)
      if (onDelete) {
        onDelete(task.id)
      }
    } catch (error) {
      console.error("Failed to delete task:", error)
      setIsDeleting(false)
    }
  }

  const handleEdit = () => {
    router.push(`/tasks/${task.id}/edit`)
  }

  return (
    <Card className={isDeleting ? "opacity-50" : ""}>
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* Checkbox */}
          <button
            onClick={handleToggleComplete}
            disabled={isToggling || isDeleting}
            className="mt-1 flex-shrink-0 focus:outline-none"
          >
            <div
              className={`flex h-5 w-5 items-center justify-center rounded border-2 transition-colors ${
                task.completed
                  ? "border-green-600 bg-green-600"
                  : "border-gray-300 hover:border-green-600"
              } ${isToggling ? "opacity-50" : ""}`}
            >
              {task.completed && (
                <svg
                  className="h-3 w-3 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={3}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
            </div>
          </button>

          {/* Task Content */}
          <div className="flex-1 min-w-0">
            <h3
              className={`text-base font-medium ${
                task.completed
                  ? "text-gray-400 line-through"
                  : "text-gray-900"
              }`}
            >
              {task.title}
            </h3>
            {task.description && (
              <p
                className={`mt-1 text-sm ${
                  task.completed ? "text-gray-400" : "text-gray-600"
                }`}
              >
                {task.description}
              </p>
            )}
            <p className="mt-2 text-xs text-gray-500">
              Created {formatDate(task.created_at)}
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleEdit}
              disabled={isDeleting}
            >
              Edit
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
