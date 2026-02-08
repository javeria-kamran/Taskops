/**
 * New task creation page
 */

import { TaskForm } from "@/components/tasks/task-form"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

export const metadata = {
  title: "New Task - taskops",
  description: "Create a new task",
}

export default function NewTaskPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Create New Task</h1>
        <p className="mt-2 text-sm text-gray-600">
          Add a new task to your todo list
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Task Details</CardTitle>
          <CardDescription>
            Fill in the information below to create a new task
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TaskForm />
        </CardContent>
      </Card>
    </div>
  )
}
