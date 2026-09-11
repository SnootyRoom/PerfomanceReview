<script setup lang="ts">
import BaseModal from './BaseModal.vue'
import BaseButton from './BaseButton.vue'
import { confirmState } from '@/composables/useConfirm'

function answer(value: boolean) {
  confirmState.request?.resolve(value)
  confirmState.request = null
}
</script>

<template>
  <BaseModal v-if="confirmState.request" :title="confirmState.request.title" @close="answer(false)">
    <p>{{ confirmState.request.message }}</p>
    <template #footer>
      <BaseButton variant="secondary" @click="answer(false)">Отмена</BaseButton>
      <BaseButton :variant="confirmState.request.danger ? 'danger' : 'primary'" @click="answer(true)">
        {{ confirmState.request.confirmLabel }}
      </BaseButton>
    </template>
  </BaseModal>
</template>
