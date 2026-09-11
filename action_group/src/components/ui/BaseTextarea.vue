<script setup lang="ts">
const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    label?: string
    placeholder?: string
    hint?: string
    rows?: number
  }>(),
  { rows: 5 },
)
</script>

<template>
  <label class="field">
    <span v-if="label" class="field__label">{{ label }}</span>
    <textarea v-model="model" class="field__input" :placeholder="placeholder" :rows="rows" />
    <span v-if="hint" class="field__hint">{{ hint }}</span>
  </label>
</template>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.field__label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-muted);
}

.field__input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
}

.field__input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.field__hint {
  font-size: 12px;
  color: var(--color-text-faint);
}
</style>
