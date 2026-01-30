<script setup lang="ts">
import type { Task } from '../types'
import StatusBadge from './StatusBadge.vue'

const props = defineProps<{
  tasks: Task[]
  runningTasks: Set<string>
}>()

const emit = defineEmits<{
  run: [task: Task]
  edit: [task: Task]
  delete: [task: Task]
  toggle: [task: Task]
  duplicate: [task: Task]
}>()

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

function getTaskStatus(task: Task): 'running' | 'idle' {
  return props.runningTasks.has(task.id) ? 'running' : 'idle'
}
</script>

<template>
  <div class="task-table-container">
    <table class="task-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Schedule</th>
          <th>Status</th>
          <th>Enabled</th>
          <th>Last Run</th>
          <th>Next Run</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in tasks" :key="task.id">
          <td class="task-name">
            <div>{{ task.name }}</div>
            <div class="task-description">{{ task.description.slice(0, 60) }}...</div>
          </td>
          <td class="cron">
            <span v-if="task.cron_expression">{{ task.cron_expression }}</span>
            <span v-else class="manual-badge">Manual</span>
          </td>
          <td>
            <StatusBadge :status="getTaskStatus(task)" />
          </td>
          <td>
            <StatusBadge :status="task.is_enabled ? 'enabled' : 'disabled'" />
          </td>
          <td class="date">{{ formatDate(task.last_run_at) }}</td>
          <td class="date">
            <span v-if="task.cron_expression">{{ formatDate(task.next_run_at) }}</span>
            <span v-else class="manual-only">-</span>
          </td>
          <td class="actions">
            <button
              class="btn btn-run btn-sm"
              @click="emit('run', task)"
              :disabled="runningTasks.has(task.id)"
              :title="runningTasks.has(task.id) ? 'Task is running' : 'Run task now'"
            >
              <span class="play-icon">▶</span>
              {{ runningTasks.has(task.id) ? 'Running...' : 'Run' }}
            </button>
            <button class="btn btn-secondary btn-sm" @click="emit('edit', task)">
              Edit
            </button>
            <button class="btn btn-secondary btn-sm" @click="emit('duplicate', task)">
              Duplicate
            </button>
            <button class="btn btn-secondary btn-sm" @click="emit('toggle', task)">
              {{ task.is_enabled ? 'Disable' : 'Enable' }}
            </button>
            <button class="btn btn-danger btn-sm" @click="emit('delete', task)">
              Delete
            </button>
          </td>
        </tr>
        <tr v-if="tasks.length === 0">
          <td colspan="7" class="empty">
            No tasks configured. Create one to get started.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.task-table-container {
  overflow-x: auto;
}

.task-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.task-table th,
.task-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.task-table th {
  background: #f9fafb;
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
}

.task-name {
  max-width: 250px;
}

.task-name > div:first-child {
  font-weight: 500;
}

.task-description {
  font-size: 0.75rem;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cron {
  font-family: monospace;
  font-size: 0.875rem;
}

.date {
  font-size: 0.875rem;
  color: #6b7280;
  white-space: nowrap;
}

.actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-run {
  background: #22c55e;
  color: white;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.btn-run:hover:not(:disabled) {
  background: #16a34a;
}

.play-icon {
  font-size: 0.625rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.manual-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background: #e0e7ff;
  color: #4338ca;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.manual-only {
  color: #9ca3af;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-danger {
  background: #fee2e2;
  color: #b91c1c;
}

.btn-danger:hover:not(:disabled) {
  background: #fecaca;
}

.empty {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}
</style>
