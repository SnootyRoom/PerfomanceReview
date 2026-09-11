<script setup lang="ts">
const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    label?: string
    error?: string
    required?: boolean
    disabled?: boolean
    options: { value: string; label: string }[]
    placeholder?: string
  }>(),
  { required: false, disabled: false },
)
</script>

<template>
  <label class="field">
    <span v-if="label" class="field__label">{{ label }}<span v-if="required" class="field__required">*</span></span>
    <select v-model="model" class="field__input" :class="{ 'field__input--error': error }" :disabled="disabled">
      <option v-if="placeholder" value="">{{ placeholder }}</option>
      <option v-for="opt in options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
    </select>
    <span v-if="error" class="field__error">{{ error }}</span>
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
}

.field__input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.field__input--error {
  border-color: var(--color-danger);
}

.field__error {
  font-size: 12px;
  color: var(--color-danger);
}
</style>
