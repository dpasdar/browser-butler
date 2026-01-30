<script setup lang="ts">
defineProps<{
  status: 'running' | 'success' | 'failure' | 'timeout' | 'idle' | 'enabled' | 'disabled'
}>()
</script>

<template>
  <span class="badge" :class="status">
    {{ status }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.running {
  background: #dbeafe;
  color: #1d4ed8;
}

.success {
  background: #dcfce7;
  color: #166534;
}

.failure {
  background: #fee2e2;
  color: #b91c1c;
}

.timeout {
  background: #fef3c7;
  color: #92400e;
}

.idle {
  background: #f3f4f6;
  color: #6b7280;
}

.enabled {
  background: #dcfce7;
  color: #166534;
}

.disabled {
  background: #f3f4f6;
  color: #6b7280;
}
</style>
