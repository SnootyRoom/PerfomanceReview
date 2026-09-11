<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    value: number // 0..100
    variant?: 'primary' | 'success' | 'warning' | 'danger'
    size?: 'sm' | 'md'
  }>(),
  { variant: 'primary', size: 'md' },
)

const clamped = computed(() => Math.max(0, Math.min(100, props.value)))
</script>

<template>
  <div class="progress" :class="`progress--${size}`" role="progressbar" :aria-valuenow="clamped" aria-valuemin="0" aria-valuemax="100">
    <div class="progress__fill" :class="`progress__fill--${variant}`" :style="{ width: clamped + '%' }" />
  </div>
</template>

<style scoped>
.progress {
  width: 100%;
  background: var(--color-surface-alt);
  border-radius: 999px;
  overflow: hidden;
}

.progress--md {
  height: 8px;
}
.progress--sm {
  height: 5px;
}

.progress__fill {
  height: 100%;
  border-radius: inherit;
  transition: width 0.3s ease;
}

.progress__fill--primary {
  background: var(--color-primary);
}
.progress__fill--success {
  background: var(--color-success);
}
.progress__fill--warning {
  background: var(--color-warning);
}
.progress__fill--danger {
  background: var(--color-danger);
}
</style>
