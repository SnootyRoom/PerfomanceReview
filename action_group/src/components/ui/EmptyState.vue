<script setup lang="ts">
import type { Component } from 'vue'
import { Inbox } from '@lucide/vue'

const props = defineProps<{ icon?: Component; title: string; description?: string }>()
</script>

<template>
  <div class="empty">
    <component :is="props.icon ?? Inbox" :size="32" class="empty__icon" stroke-width="1.5" />
    <p class="empty__title">{{ title }}</p>
    <p v-if="description" class="empty__desc">{{ description }}</p>
    <div v-if="$slots.action" class="empty__action"><slot name="action" /></div>
  </div>
</template>

<style scoped>
.empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-text-muted);
}
.empty__icon {
  margin-bottom: 10px;
  color: var(--color-text-faint);
}
.empty__title {
  font-weight: 600;
  color: var(--color-text);
}
.empty__desc {
  font-size: 13px;
  margin-top: 4px;
}
.empty__action {
  margin-top: 14px;
}
</style>
