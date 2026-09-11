<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
    size?: 'sm' | 'md'
    type?: 'button' | 'submit'
    disabled?: boolean
    loading?: boolean
    block?: boolean
  }>(),
  {
    variant: 'primary',
    size: 'md',
    type: 'button',
    disabled: false,
    loading: false,
    block: false,
  },
)
</script>

<template>
  <button
    :type="type"
    class="btn"
    :class="[`btn--${variant}`, `btn--${size}`, { 'btn--block': block }]"
    :disabled="disabled || loading"
  >
    <span v-if="loading" class="btn__spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition:
    background-color 0.15s,
    border-color 0.15s,
    opacity 0.15s;
}

.btn--md {
  padding: 10px 16px;
  font-size: 14px;
}
.btn--sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn--block {
  width: 100%;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn--primary {
  background: var(--color-primary);
  color: var(--color-primary-contrast);
}
.btn--primary:not(:disabled):hover {
  background: var(--color-primary-hover);
}

.btn--secondary {
  background: var(--color-surface);
  border-color: var(--color-border);
  color: var(--color-text);
}
.btn--secondary:not(:disabled):hover {
  background: var(--color-surface-alt);
}

.btn--ghost {
  background: transparent;
  color: var(--color-text-muted);
}
.btn--ghost:not(:disabled):hover {
  background: var(--color-surface-alt);
  color: var(--color-text);
}

.btn--danger {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}
.btn--danger:not(:disabled):hover {
  background: var(--color-danger);
  color: white;
}

.btn__spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid currentColor;
  border-right-color: transparent;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
