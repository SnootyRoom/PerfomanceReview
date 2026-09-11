<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string
    value: number // 0..100
    sub?: string
    color?: string
  }>(),
  { color: 'var(--color-primary)' },
)
</script>

<template>
  <div class="bar-row">
    <div class="bar-row__head">
      <span class="bar-row__label">{{ label }}</span>
      <span class="bar-row__value">{{ Math.round(value) }}%<template v-if="sub"> · {{ sub }}</template></span>
    </div>
    <div class="bar-row__track">
      <div class="bar-row__fill" :style="{ width: Math.max(0, Math.min(100, value)) + '%', background: color }" />
    </div>
  </div>
</template>

<style scoped>
.bar-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.bar-row__head {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}
.bar-row__label {
  font-weight: 600;
}
.bar-row__value {
  color: var(--color-text-muted);
}
.bar-row__track {
  height: 9px;
  border-radius: 999px;
  background: var(--color-surface-alt);
  overflow: hidden;
}
.bar-row__fill {
  height: 100%;
  border-radius: inherit;
  transition: width 0.3s ease;
}
</style>
