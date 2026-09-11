<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { X } from '@lucide/vue'

const props = withDefaults(
  defineProps<{
    title?: string
    wide?: boolean
  }>(),
  { wide: false },
)

const emit = defineEmits<{ close: [] }>()

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Teleport to="body">
    <div class="overlay" @mousedown.self="emit('close')">
      <div class="modal" :class="{ 'modal--wide': props.wide }" role="dialog" aria-modal="true">
        <header class="modal__header">
          <h2 class="modal__title">{{ props.title }}</h2>
          <button class="modal__close" type="button" aria-label="Закрыть" @click="emit('close')">
            <X :size="15" />
          </button>
        </header>
        <div class="modal__body">
          <slot />
        </div>
        <footer v-if="$slots.footer" class="modal__footer">
          <slot name="footer" />
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 16, 26, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 900;
  padding: 0;
}

.modal {
  background: var(--color-surface);
  width: 100%;
  max-height: 92vh;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

@media (min-width: 640px) {
  .overlay {
    align-items: center;
    padding: 20px;
  }
  .modal {
    max-width: 520px;
    max-height: 85vh;
    border-radius: var(--radius-lg);
  }
  .modal--wide {
    max-width: 760px;
  }
}

.modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.modal__title {
  font-size: 17px;
  font-weight: 700;
}

.modal__close {
  border: none;
  background: var(--color-surface-alt);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal__body {
  padding: 20px;
  overflow-y: auto;
}

.modal__footer {
  padding: 14px 20px;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-shrink: 0;
}
</style>
