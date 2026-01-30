<script setup lang="ts">
import { ref } from 'vue'
import type { TaskLog } from '../types'
import StatusBadge from './StatusBadge.vue'

defineProps<{
  logs: TaskLog[]
}>()

const expandedLog = ref<string | null>(null)

function toggleExpand(logId: string) {
  expandedLog.value = expandedLog.value === logId ? null : logId
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return '-'
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}m ${secs.toFixed(0)}s`
}
</script>

<template>
  <div class="log-table-container">
    <table class="log-table">
      <thead>
        <tr>
          <th></th>
          <th>Task</th>
          <th>Status</th>
          <th>Started</th>
          <th>Duration</th>
          <th>Result</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="log in logs" :key="log.id">
          <tr @click="toggleExpand(log.id)" class="log-row">
            <td class="expand-cell">
              <span class="expand-icon" :class="{ expanded: expandedLog === log.id }">
                ▶
              </span>
            </td>
            <td>{{ log.task_name || log.task_id }}</td>
            <td>
              <StatusBadge :status="log.status" />
            </td>
            <td class="date">{{ formatDate(log.started_at) }}</td>
            <td>{{ formatDuration(log.duration_seconds) }}</td>
            <td class="result">
              <template v-if="log.status === 'success'">
                {{ log.result_summary?.slice(0, 50) }}...
              </template>
              <template v-else-if="log.error_message">
                {{ log.error_message.slice(0, 50) }}...
              </template>
              <template v-else>-</template>
            </td>
          </tr>
          <tr v-if="expandedLog === log.id" class="expanded-row">
            <td colspan="6">
              <div class="log-details">
                <div v-if="log.result_summary" class="detail-section">
                  <h4>Result Summary</h4>
                  <pre>{{ log.result_summary }}</pre>
                </div>
                <div v-if="log.error_message" class="detail-section error">
                  <h4>Error</h4>
                  <pre>{{ log.error_message }}</pre>
                </div>
                <div v-if="log.agent_steps && log.agent_steps.length > 0" class="detail-section">
                  <h4>Agent Steps</h4>
                  <div class="steps">
                    <div v-for="step in log.agent_steps" :key="step.index" class="step">
                      <span class="step-index">{{ step.index + 1 }}.</span>
                      <span v-if="step.action" class="step-action">{{ step.action }}</span>
                      <span v-if="step.result" class="step-result">→ {{ step.result }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </template>
        <tr v-if="logs.length === 0">
          <td colspan="6" class="empty">
            No logs found.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.log-table-container {
  overflow-x: auto;
}

.log-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.log-table th,
.log-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.log-table th {
  background: #f9fafb;
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
}

.log-row {
  cursor: pointer;
  transition: background 0.2s;
}

.log-row:hover {
  background: #f9fafb;
}

.expand-cell {
  width: 30px;
}

.expand-icon {
  display: inline-block;
  transition: transform 0.2s;
  color: #9ca3af;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.date {
  font-size: 0.875rem;
  color: #6b7280;
  white-space: nowrap;
}

.result {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.875rem;
}

.expanded-row td {
  padding: 0;
  background: #f9fafb;
}

.log-details {
  padding: 1rem;
}

.detail-section {
  margin-bottom: 1rem;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #374151;
}

.detail-section pre {
  background: white;
  padding: 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-section.error pre {
  background: #fee2e2;
  color: #b91c1c;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.step {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
  font-size: 0.875rem;
}

.step-index {
  color: #9ca3af;
  font-weight: 500;
}

.step-action {
  color: #374151;
}

.step-result {
  color: #059669;
}

.empty {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}
</style>
