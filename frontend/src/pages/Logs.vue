<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { TaskLog } from '../types'
import { getLogs, getTasks } from '../api'
import LogTable from '../components/LogTable.vue'

const route = useRoute()

const logs = ref<TaskLog[]>([])
const tasks = ref<{ id: string; name: string }[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const page = ref(1)
const perPage = ref(25)
const totalPages = ref(1)
const total = ref(0)

const filterTaskId = ref<string>('')
const filterStatus = ref<string>('')

const taskIdFromRoute = computed(() => route.params.taskId as string | undefined)

onMounted(async () => {
  await loadTasks()
  if (taskIdFromRoute.value) {
    filterTaskId.value = taskIdFromRoute.value
  }
  await loadLogs()
})

watch([filterTaskId, filterStatus], () => {
  page.value = 1
  loadLogs()
})

watch(taskIdFromRoute, (newVal) => {
  filterTaskId.value = newVal || ''
})

async function loadTasks() {
  try {
    const response = await getTasks()
    tasks.value = response.tasks.map((t) => ({ id: t.id, name: t.name }))
  } catch {
    // Ignore task loading errors
  }
}

async function loadLogs() {
  try {
    loading.value = true
    error.value = null

    const response = await getLogs({
      task_id: filterTaskId.value || undefined,
      status: filterStatus.value || undefined,
      page: page.value,
      per_page: perPage.value,
    })

    logs.value = response.logs
    total.value = response.total
    totalPages.value = response.total_pages
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load logs'
  } finally {
    loading.value = false
  }
}

function prevPage() {
  if (page.value > 1) {
    page.value--
    loadLogs()
  }
}

function nextPage() {
  if (page.value < totalPages.value) {
    page.value++
    loadLogs()
  }
}
</script>

<template>
  <div class="logs-page">
    <header class="page-header">
      <h1>Execution Logs</h1>
    </header>

    <div class="filters">
      <div class="filter-group">
        <label for="filter-task">Task</label>
        <select id="filter-task" v-model="filterTaskId">
          <option value="">All Tasks</option>
          <option v-for="task in tasks" :key="task.id" :value="task.id">
            {{ task.name }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label for="filter-status">Status</label>
        <select id="filter-status" v-model="filterStatus">
          <option value="">All Statuses</option>
          <option value="running">Running</option>
          <option value="success">Success</option>
          <option value="failure">Failure</option>
          <option value="timeout">Timeout</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else>
      <LogTable :logs="logs" />

      <div class="pagination" v-if="totalPages > 1">
        <button class="btn btn-secondary" @click="prevPage" :disabled="page <= 1">
          Previous
        </button>
        <span class="page-info">
          Page {{ page }} of {{ totalPages }} ({{ total }} total)
        </span>
        <button
          class="btn btn-secondary"
          @click="nextPage"
          :disabled="page >= totalPages"
        >
          Next
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.logs-page {
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

.filters {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-group label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
}

.filter-group select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.875rem;
  min-width: 150px;
}

.filter-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
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

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}
</style>
