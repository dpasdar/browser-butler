<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { Task, TaskCreate } from '../types'
import { getTask, createTask, updateTask } from '../api'
import CronInput from '../components/CronInput.vue'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const taskId = computed(() => route.params.id as string | undefined)

const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)

const useSchedule = ref(false)

const form = ref<TaskCreate>({
  name: '',
  description: '',
  cron_expression: '0 * * * *',
  timezone: 'UTC',
  timeout_seconds: 300,
  headless: true,
  start_url: '',
  telegram_enabled: true,
  telegram_chat_id: '',
  notify_on_success: false,
  notify_on_failure: true,
})

onMounted(async () => {
  if (isEdit.value && taskId.value) {
    await loadTask(taskId.value)
  }
})

async function loadTask(id: string) {
  try {
    loading.value = true
    error.value = null
    const task = await getTask(id)
    useSchedule.value = !!task.cron_expression
    form.value = {
      name: task.name,
      description: task.description,
      cron_expression: task.cron_expression || '0 * * * *',
      timezone: task.timezone,
      timeout_seconds: task.timeout_seconds,
      headless: task.headless,
      start_url: task.start_url || '',
      telegram_enabled: task.telegram_enabled,
      telegram_chat_id: task.telegram_chat_id || '',
      notify_on_success: task.notify_on_success,
      notify_on_failure: task.notify_on_failure,
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load task'
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  try {
    saving.value = true
    error.value = null

    const data = {
      ...form.value,
      cron_expression: useSchedule.value ? form.value.cron_expression : null,
      start_url: form.value.start_url || null,
      telegram_chat_id: form.value.telegram_chat_id || null,
    }

    if (isEdit.value && taskId.value) {
      await updateTask(taskId.value, data)
    } else {
      await createTask(data)
    }

    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to save task'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="task-config">
    <header class="page-header">
      <h1>{{ isEdit ? 'Edit Task' : 'Create Task' }}</h1>
    </header>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error && loading" class="error">{{ error }}</div>

    <form v-else @submit.prevent="handleSubmit" class="form">
      <div v-if="error" class="form-error">{{ error }}</div>

      <div class="form-section">
        <h2>Basic Information</h2>

        <div class="form-group">
          <label for="name">Name</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            required
            placeholder="My Automation Task"
          />
        </div>

        <div class="form-group">
          <label for="description">Task Description</label>
          <textarea
            id="description"
            v-model="form.description"
            required
            rows="4"
            placeholder="Describe what the AI agent should do, e.g., 'Go to example.com and take a screenshot of the homepage'"
          ></textarea>
          <span class="help-text">
            Use natural language to describe the browser automation task
          </span>
        </div>

        <div class="form-group">
          <label for="start_url">Start URL (optional)</label>
          <input
            id="start_url"
            v-model="form.start_url"
            type="url"
            placeholder="https://example.com"
          />
          <span class="help-text">
            Optional starting URL for the browser
          </span>
        </div>
      </div>

      <div class="form-section">
        <h2>Schedule</h2>

        <div class="form-group checkbox-group">
          <label>
            <input type="checkbox" v-model="useSchedule" />
            Enable scheduled runs
          </label>
          <span class="help-text">
            Disable to create a manual-only task that you trigger with the Run button
          </span>
        </div>

        <template v-if="useSchedule">
          <div class="form-group">
            <label>Cron Expression</label>
            <CronInput v-model="form.cron_expression" />
          </div>

          <div class="form-group">
            <label for="timezone">Timezone</label>
            <select id="timezone" v-model="form.timezone">
              <option value="UTC">UTC</option>
              <option value="America/New_York">Eastern Time</option>
              <option value="America/Chicago">Central Time</option>
              <option value="America/Denver">Mountain Time</option>
              <option value="America/Los_Angeles">Pacific Time</option>
              <option value="Europe/London">London</option>
              <option value="Europe/Paris">Paris</option>
              <option value="Asia/Tokyo">Tokyo</option>
            </select>
          </div>
        </template>

        <div v-else class="manual-info">
          <span class="manual-icon">▶</span>
          <span>This task will only run when you click the <strong>Run</strong> button</span>
        </div>
      </div>

      <div class="form-section">
        <h2>Execution Settings</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="timeout">Timeout (seconds)</label>
            <input
              id="timeout"
              v-model.number="form.timeout_seconds"
              type="number"
              min="30"
              max="3600"
            />
          </div>

          <div class="form-group checkbox-group">
            <label>
              <input type="checkbox" v-model="form.headless" />
              Run in headless mode
            </label>
            <span class="help-text">
              Disable to see the browser window during execution
            </span>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h2>Telegram Notifications</h2>

        <div class="form-group checkbox-group">
          <label>
            <input type="checkbox" v-model="form.telegram_enabled" />
            Enable Telegram notifications
          </label>
        </div>

        <template v-if="form.telegram_enabled">
          <div class="form-group">
            <label for="telegram_chat_id">Chat ID (optional)</label>
            <input
              id="telegram_chat_id"
              v-model="form.telegram_chat_id"
              type="text"
              placeholder="Leave empty to use default"
            />
            <span class="help-text">
              Override the default chat ID for this task
            </span>
          </div>

          <div class="form-row">
            <div class="form-group checkbox-group">
              <label>
                <input type="checkbox" v-model="form.notify_on_success" />
                Notify on success
              </label>
            </div>

            <div class="form-group checkbox-group">
              <label>
                <input type="checkbox" v-model="form.notify_on_failure" />
                Notify on failure
              </label>
            </div>
          </div>
        </template>
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="router.back()">
          Cancel
        </button>
        <button type="submit" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Saving...' : (isEdit ? 'Update Task' : 'Create Task') }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.task-config {
  max-width: 800px;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.loading,
.error {
  padding: 2rem;
  text-align: center;
  background: white;
  border-radius: 8px;
}

.error {
  color: #b91c1c;
  background: #fee2e2;
}

.form {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-error {
  padding: 1rem;
  background: #fee2e2;
  color: #b91c1c;
  border-bottom: 1px solid #fecaca;
}

.form-section {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.25rem;
}

.form-group input[type="text"],
.form-group input[type="url"],
.form-group input[type="number"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.form-group textarea {
  resize: vertical;
}

.help-text {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row .form-group {
  flex: 1;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
}

.form-actions {
  padding: 1rem 1.5rem;
  background: #f9fafb;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  border-radius: 0 0 8px 8px;
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

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.manual-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  color: #166534;
  margin-top: 1rem;
}

.manual-icon {
  font-size: 1.25rem;
  color: #22c55e;
}
</style>
