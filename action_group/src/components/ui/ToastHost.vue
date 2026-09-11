<script setup lang="ts">
import { toasts } from '@/composables/useToast'
</script>

<template>
  <div class="toast-host">
    <TransitionGroup name="toast">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="`toast--${t.kind}`">
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-host {
  position: fixed;
  z-index: 1000;
  left: 50%;
  bottom: calc(var(--bottom-nav-height, 0px) + 16px);
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: min(92vw, 380px);
}

@media (min-width: 861px) {
  .toast-host {
    bottom: 20px;
  }
}

.toast {
  padding: 12px 16px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  font-size: 14px;
  color: white;
  background: #303244;
  text-align: center;
}

.toast--success {
  background: var(--color-success);
}
.toast--error {
  background: var(--color-danger);
}
.toast--info {
  background: var(--color-info);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.2s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
