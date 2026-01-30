import type { Task, TaskCreate, TaskLog, LogListResponse } from './types'

const BASE_URL = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

// Tasks
export async function getTasks(): Promise<{ tasks: Task[]; total: number }> {
  return request('/tasks')
}

export async function getTask(id: string): Promise<Task> {
  return request(`/tasks/${id}`)
}

export async function createTask(task: TaskCreate): Promise<Task> {
  return request('/tasks', {
    method: 'POST',
    body: JSON.stringify(task),
  })
}

export async function updateTask(id: string, task: Partial<TaskCreate>): Promise<Task> {
  return request(`/tasks/${id}`, {
    method: 'PUT',
    body: JSON.stringify(task),
  })
}

export async function deleteTask(id: string): Promise<void> {
  return request(`/tasks/${id}`, { method: 'DELETE' })
}

export async function runTask(id: string): Promise<{ message: string; task_id: string }> {
  return request(`/tasks/${id}/run`, { method: 'POST' })
}

export async function toggleTask(id: string): Promise<Task> {
  return request(`/tasks/${id}/toggle`, { method: 'POST' })
}

export async function duplicateTask(id: string): Promise<Task> {
  return request(`/tasks/${id}/duplicate`, { method: 'POST' })
}

// Logs
export async function getLogs(params?: {
  task_id?: string
  status?: string
  page?: number
  per_page?: number
}): Promise<LogListResponse> {
  const searchParams = new URLSearchParams()
  if (params?.task_id) searchParams.set('task_id', params.task_id)
  if (params?.status) searchParams.set('status', params.status)
  if (params?.page) searchParams.set('page', params.page.toString())
  if (params?.per_page) searchParams.set('per_page', params.per_page.toString())

  const query = searchParams.toString()
  return request(`/logs${query ? `?${query}` : ''}`)
}

export async function getLog(id: string): Promise<TaskLog> {
  return request(`/logs/${id}`)
}

// System
export async function getSystemStatus(): Promise<{
  scheduler: { running: boolean; scheduled_jobs: number }
  running_tasks: Record<string, string>
  sse_subscribers: number
  config: { telegram_configured: boolean; openai_configured: boolean }
}> {
  return request('/system/status')
}
