<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import { ClipboardCheck } from '@lucide/vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const login = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

async function submit() {
  error.value = ''
  submitting.value = true
  try {
    await auth.login(login.value.trim(), password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.push(redirect)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Не удалось войти'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="login">
    <form class="login__card" @submit.prevent="submit">
      <div class="login__logo"><ClipboardCheck :size="22" /></div>
      <h1 class="login__title">Performance Review</h1>
      <p class="login__subtitle">Система мониторинга развития технических навыков команды</p>

      <div class="stack gap-md">
        <BaseInput v-model="login" label="Логин" placeholder="Введите логин" required autocomplete="username" />
        <BaseInput
          v-model="password"
          label="Пароль"
          type="password"
          placeholder="••••••"
          required
          autocomplete="current-password"
        />
      </div>

      <p v-if="error" class="login__error">{{ error }}</p>

      <BaseButton type="submit" block :loading="submitting">Войти</BaseButton>
    </form>
  </div>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background:
    radial-gradient(circle at top left, var(--color-primary-soft), transparent 55%),
    var(--color-bg);
}

.login__card {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 32px 28px;
}

.login__logo {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--color-primary);
  color: white;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.login__title {
  font-size: 20px;
  font-weight: 800;
}

.login__subtitle {
  color: var(--color-text-muted);
  font-size: 13.5px;
  margin-top: 6px;
  margin-bottom: 22px;
}

.login__error {
  color: var(--color-danger);
  font-size: 13px;
  margin-top: 12px;
}

.login :deep(.btn) {
  margin-top: 20px;
}
</style>
