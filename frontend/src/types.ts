export interface Task {
  id: string
  name: string
  description: string
  cron_expression: string | null
  timezone: string
  is_enabled: boolean
  timeout_seconds: number
  headless: boolean
  start_url: string | null
  telegram_enabled: boolean
  telegram_chat_id: string | null
  notify_on_success: boolean
  notify_on_failure: boolean
  created_at: string
  updated_at: string
  last_run_at: string | null
  next_run_at: string | null
}

export interface TaskCreate {
  name: string
  description: string
  cron_expression?: string | null
  timezone?: string
  timeout_seconds?: number
  headless?: boolean
  start_url?: string | null
  telegram_enabled?: boolean
  telegram_chat_id?: string | null
  notify_on_success?: boolean
  notify_on_failure?: boolean
}

export interface TaskLog {
  id: string
  task_id: string
  task_name: string | null
  status: 'running' | 'success' | 'failure' | 'timeout'
  started_at: string
  completed_at: string | null
  duration_seconds: number | null
  result_summary: string | null
  error_message: string | null
  agent_steps: Array<{ index: number; action?: string; result?: string }> | null
  created_at: string
}

export interface LogListResponse {
  logs: TaskLog[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface SSEEvent {
  type: 'task_started' | 'task_completed'
  task_id: string
  log_id: string
  status?: string
}
