<script setup lang="ts">
const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    label?: string
    type?: string
    placeholder?: string
    error?: string
    hint?: string
    required?: boolean
    disabled?: boolean
  }>(),
  { type: 'text', required: false, disabled: false },
)

defineOptions({ inheritAttrs: false })
</script>

<template>
  <label class="field">
    <span v-if="label" class="field__label">{{ label }}<span v-if="required" class="field__required">*</span></span>
    <input
      v-model="model"
      class="field__input"
      :class="{ 'field__input--error': error }"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      v-bind="$attrs"
    />
    <span v-if="error" class="field__error">{{ error }}</span>
    <span v-else-if="hint" class="field__hint">{{ hint }}</span>
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

.field__required {
  color: var(--color-danger);
  margin-left: 2px;
}

.field__input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 14px;
  transition: border-color 0.15s;
}

.field__input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.field__input--error {
  border-color: var(--color-danger);
}

.field__input:disabled {
  opacity: 0.6;
}

.field__error {
  font-size: 12px;
  color: var(--color-danger);
}

.field__hint {
  font-size: 12px;
  color: var(--color-text-faint);
}
</style>
