<script setup lang="ts">
import { renderMarkdown } from '@/composables/useMarkdown'
import BaseModal from './BaseModal.vue'

defineProps<{ loading: boolean; error: string; text: string }>()
const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <BaseModal title="AI-анализ (GigaChat)" wide @close="emit('close')">
    <div v-if="loading" class="text-muted text-sm">Генерируем анализ…</div>
    <p v-else-if="error" class="text-sm" style="color: var(--color-danger)">{{ error }}</p>
    <div v-else class="markdown-body" v-html="renderMarkdown(text)" />
    <p v-if="!loading && !error" class="text-sm text-faint" style="margin-top: 16px">
      Сгенерировано нейросетью GigaChat, возможны неточности — проверяйте важные выводы самостоятельно.
    </p>
  </BaseModal>
</template>
