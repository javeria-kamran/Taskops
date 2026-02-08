/**
 * API client for backend communication
 */

import type { Task, TaskCreate, TaskUpdate } from "@/types/task"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

/**
 * Get authentication headers with JWT token
 */
function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("auth_token")
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

/**
 * Task API client
 */
export const tasksApi = {
  /**
   * Create a new task
   */
  async create(data: TaskCreate): Promise<Task> {
    const response = await fetch(`${BACKEND_URL}/api/tasks`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to create task")
    }

    return response.json()
  },

  /**
   * Get all tasks for the current user
   */
  async getAll(completed?: boolean): Promise<Task[]> {
    const params = new URLSearchParams()
    if (completed !== undefined) {
      params.append("completed", String(completed))
    }

    const url = `${BACKEND_URL}/api/tasks${params.toString() ? `?${params}` : ""}`
    const response = await fetch(url, {
      method: "GET",
      headers: getAuthHeaders(),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to fetch tasks")
    }

    return response.json()
  },

  /**
   * Get a specific task by ID
   */
  async getById(taskId: string): Promise<Task> {
    const response = await fetch(`${BACKEND_URL}/api/tasks/${taskId}`, {
      method: "GET",
      headers: getAuthHeaders(),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to fetch task")
    }

    return response.json()
  },

  /**
   * Update a task
   */
  async update(taskId: string, data: TaskUpdate): Promise<Task> {
    const response = await fetch(`${BACKEND_URL}/api/tasks/${taskId}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to update task")
    }

    return response.json()
  },

  /**
   * Delete a task
   */
  async delete(taskId: string): Promise<void> {
    const response = await fetch(`${BACKEND_URL}/api/tasks/${taskId}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to delete task")
    }
  },

  /**
   * Toggle task completion status
   */
  async toggleComplete(taskId: string, completed: boolean): Promise<Task> {
    return this.update(taskId, { completed })
  },
}
