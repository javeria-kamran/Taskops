/**
 * Task TypeScript interfaces for task management
 */

export interface Task {
  id: string
  user_id: string
  title: string
  description?: string
  completed: boolean
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  completed?: boolean
}

export interface TasksResponse {
  tasks: Task[]
  total: number
}
