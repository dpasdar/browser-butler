<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const connected = ref(false)
let eventSource: EventSource | null = null

onMounted(() => {
  connectSSE()
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
})

function connectSSE() {
  eventSource = new EventSource('/api/events')

  eventSource.onopen = () => {
    connected.value = true
  }

  eventSource.onerror = () => {
    connected.value = false
    setTimeout(connectSSE, 5000)
  }
}
</script>

<template>
  <div class="app">
    <nav class="navbar">
      <div class="navbar-brand">
        <RouterLink to="/">Browser Butler</RouterLink>
      </div>
      <div class="navbar-menu">
        <RouterLink to="/" class="nav-link">Dashboard</RouterLink>
        <RouterLink to="/logs" class="nav-link">Logs</RouterLink>
        <span class="connection-status" :class="{ connected }">
          {{ connected ? 'Connected' : 'Disconnected' }}
        </span>
      </div>
    </nav>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
}

.navbar {
  background: #1a1a2e;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-brand a {
  color: white;
  text-decoration: none;
  font-size: 1.25rem;
  font-weight: 600;
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.nav-link:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  color: white;
  background: rgba(255, 255, 255, 0.15);
}

.connection-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  background: #ef4444;
}

.connection-status.connected {
  background: #22c55e;
}

.main-content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}
</style>
