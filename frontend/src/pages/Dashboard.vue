<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import type { Task, SSEEvent } from '../types'
import { getTasks, runTask, deleteTask, toggleTask, duplicateTask } from '../api'
import TaskTable from '../components/TaskTable.vue'

const router = useRouter()
const tasks = ref<Task[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const runningTasks = ref<Set<string>>(new Set())

let eventSource: EventSource | null = null

onMounted(async () => {
  await loadTasks()
  connectSSE()
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})

async function loadTasks() {
  try {
    loading.value = true
    error.value = null
    const response = await getTasks()
    tasks.value = response.tasks
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load tasks'
  } finally {
    loading.value = false
  }
}

function connectSSE() {
  eventSource = new EventSource('/api/events')

  eventSource.onmessage = (event) => {
    try {
      const data: SSEEvent = JSON.parse(event.data)

      if (data.type === 'task_started') {
        runningTasks.value.add(data.task_id)
      } else if (data.type === 'task_completed') {
        runningTasks.value.delete(data.task_id)
        // Refresh tasks to get updated last_run_at
        loadTasks()
      }
    } catch {
      // Ignore parse errors
    }
  }
}

async function handleRun(task: Task) {
  try {
    await runTask(task.id)
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Failed to run task')
  }
}

function handleEdit(task: Task) {
  router.push({ name: 'task-edit', params: { id: task.id } })
}

async function handleDelete(task: Task) {
  if (!confirm(`Are you sure you want to delete "${task.name}"?`)) {
    return
  }

  try {
    await deleteTask(task.id)
    await loadTasks()
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Failed to delete task')
  }
}

async function handleToggle(task: Task) {
  try {
    await toggleTask(task.id)
    await loadTasks()
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Failed to toggle task')
  }
}

async function handleDuplicate(task: Task) {
  try {
    await duplicateTask(task.id)
    await loadTasks()
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Failed to duplicate task')
  }
}
</script>

<template>
  <div class="dashboard">
    <header class="page-header">
      <h1>Tasks</h1>
      <router-link to="/tasks/new" class="btn btn-primary">
        Create Task
      </router-link>
    </header>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <TaskTable
      v-else
      :tasks="tasks"
      :running-tasks="runningTasks"
      @run="handleRun"
      @edit="handleEdit"
      @delete="handleDelete"
      @toggle="handleToggle"
      @duplicate="handleDuplicate"
    />
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
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
</style>
