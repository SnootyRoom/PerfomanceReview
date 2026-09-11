<script setup lang="ts">
import { useRouter } from 'vue-router'
import BaseButton from '@/components/ui/BaseButton.vue'

const router = useRouter()
</script>

<template>
  <div class="notfound">
    <p class="notfound__code">404</p>
    <h1>Страница не найдена</h1>
    <BaseButton @click="router.push('/')">На главную</BaseButton>
  </div>
</template>

<style scoped>
.notfound {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-align: center;
  padding: 20px;
}
.notfound__code {
  font-size: 48px;
  font-weight: 800;
  color: var(--color-primary);
}
</style>
