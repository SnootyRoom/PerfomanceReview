<script setup lang="ts">
const model = defineModel<string>({ required: true })

defineProps<{ tabs: { value: string; label: string; count?: number }[] }>()
</script>

<template>
  <div class="tabs" role="tablist">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      type="button"
      role="tab"
      class="tabs__item"
      :class="{ 'tabs__item--active': model === tab.value }"
      :aria-selected="model === tab.value"
      @click="model = tab.value"
    >
      {{ tab.label }}
      <span v-if="tab.count !== undefined" class="tabs__count">{{ tab.count }}</span>
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  border-bottom: 1px solid var(--color-border);
  scrollbar-width: none;
}
.tabs::-webkit-scrollbar {
  display: none;
}

.tabs__item {
  flex-shrink: 0;
  border: none;
  background: transparent;
  padding: 10px 14px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tabs__item--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tabs__count {
  background: var(--color-surface-alt);
  color: var(--color-text-muted);
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 999px;
}

.tabs__item--active .tabs__count {
  background: var(--color-primary-soft);
  color: var(--color-primary);
}
</style>
