<script setup lang="ts">
import { computed } from 'vue'
import cronstrue from 'cronstrue'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const cronDescription = computed(() => {
  try {
    return cronstrue.toString(props.modelValue)
  } catch {
    return 'Invalid cron expression'
  }
})

const isValid = computed(() => {
  try {
    cronstrue.toString(props.modelValue)
    return true
  } catch {
    return false
  }
})

const presets = [
  { label: 'Every minute', value: '* * * * *' },
  { label: 'Every 5 minutes', value: '*/5 * * * *' },
  { label: 'Every hour', value: '0 * * * *' },
  { label: 'Every day at midnight', value: '0 0 * * *' },
  { label: 'Every Monday at 9am', value: '0 9 * * 1' },
]

function setPreset(value: string) {
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="cron-input">
    <div class="input-row">
      <input
        type="text"
        :value="modelValue"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        placeholder="* * * * *"
        class="cron-field"
        :class="{ invalid: !isValid && modelValue }"
      />
    </div>

    <div class="description" :class="{ invalid: !isValid }">
      {{ cronDescription }}
    </div>

    <div class="presets">
      <span class="presets-label">Presets:</span>
      <button
        v-for="preset in presets"
        :key="preset.value"
        type="button"
        class="preset-btn"
        @click="setPreset(preset.value)"
      >
        {{ preset.label }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.cron-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cron-field {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-family: monospace;
  font-size: 1rem;
}

.cron-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.cron-field.invalid {
  border-color: #ef4444;
}

.description {
  font-size: 0.875rem;
  color: #059669;
}

.description.invalid {
  color: #ef4444;
}

.presets {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.presets-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.preset-btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  background: #e5e7eb;
}
</style>
