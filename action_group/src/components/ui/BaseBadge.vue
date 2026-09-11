<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'neutral' | 'success' | 'warning' | 'danger' | 'info' | 'back' | 'front' | 'qa'
  }>(),
  { variant: 'neutral' },
)
</script>

<template>
  <span class="badge" :class="`badge--${variant}`"><slot /></span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.badge--neutral {
  background: var(--color-surface-alt);
  color: var(--color-text-muted);
}
.badge--success {
  background: var(--color-success-soft);
  color: var(--color-success);
}
.badge--warning {
  background: var(--color-warning-soft);
  color: var(--color-warning);
}
.badge--danger {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}
.badge--info {
  background: var(--color-info-soft);
  color: var(--color-info);
}
.badge--back {
  background: color-mix(in srgb, var(--color-back) 15%, transparent);
  color: var(--color-back);
}
.badge--front {
  background: color-mix(in srgb, var(--color-front) 15%, transparent);
  color: var(--color-front);
}
.badge--qa {
  background: color-mix(in srgb, var(--color-qa) 15%, transparent);
  color: var(--color-qa);
}
</style>
