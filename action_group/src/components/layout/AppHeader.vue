<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import UserAvatar from '@/components/ui/UserAvatar.vue'
import { ChevronDown, ClipboardCheck, LogOut, UserRound } from '@lucide/vue'
import { adminNav } from './navItems'

const auth = useAuthStore()
const router = useRouter()
const menuOpen = ref(false)
const rootEl = ref<HTMLElement | null>(null)

function onDocClick(e: MouseEvent) {
  if (rootEl.value && !rootEl.value.contains(e.target as Node)) menuOpen.value = false
}

onMounted(() => document.addEventListener('click', onDocClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))

async function logout() {
  await auth.logout()
  menuOpen.value = false
  router.push({ name: 'login' })
}

function goProfile() {
  menuOpen.value = false
  if (auth.currentUser) router.push({ name: 'employee-profile', params: { id: auth.currentUser.id } })
}
</script>

<template>
  <header class="header">
    <div class="header__inner container">
      <router-link to="/" class="header__brand">
        <span class="header__logo"><ClipboardCheck :size="17" /></span>
        <span class="header__title">Performance Review</span>
      </router-link>

      <div ref="rootEl" class="header__user">
        <button class="header__user-btn" type="button" @click="menuOpen = !menuOpen">
          <UserAvatar
            v-if="auth.currentUser"
            :name="auth.currentUser.fullName"
            :color="auth.currentUser.avatarColor"
            :size="32"
          />
          <span class="header__user-name">{{ auth.currentUser?.fullName }}</span>
          <ChevronDown :size="14" class="header__caret" />
        </button>

        <div v-if="menuOpen" class="header__menu">
          <button type="button" class="header__menu-item" @click="goProfile">
            <UserRound :size="16" /> Мой профиль
          </button>
          <template v-if="auth.isAdmin">
            <router-link
              v-for="item in adminNav"
              :key="item.to"
              :to="item.to"
              class="header__menu-item header__menu-item--mobile-only"
              @click="menuOpen = false"
            >
              <component :is="item.icon" :size="16" /> {{ item.label }}
            </router-link>
          </template>
          <button type="button" class="header__menu-item header__menu-item--danger" @click="logout">
            <LogOut :size="16" /> Выйти
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  height: var(--header-height);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.header__inner {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--color-text);
}

.header__logo {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header__title {
  font-weight: 700;
  font-size: 15px;
}

@media (max-width: 560px) {
  .header__title {
    display: none;
  }
}

.header__user {
  position: relative;
}

.header__user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: var(--radius-md);
  color: var(--color-text);
}

.header__user-btn:hover {
  background: var(--color-surface-alt);
}

.header__user-name {
  font-size: 13px;
  font-weight: 600;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 560px) {
  .header__user-name {
    display: none;
  }
}

.header__caret {
  color: var(--color-text-faint);
  flex-shrink: 0;
}

.header__menu {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  min-width: 200px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.header__menu-item {
  display: flex;
  align-items: center;
  gap: 9px;
  text-align: left;
  width: 100%;
  border: none;
  background: transparent;
  padding: 9px 10px;
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  color: var(--color-text);
  cursor: pointer;
  text-decoration: none;
}

.header__menu-item:hover {
  background: var(--color-surface-alt);
}

.header__menu-item--danger {
  color: var(--color-danger);
}

@media (min-width: 861px) {
  .header__menu-item--mobile-only {
    display: none;
  }
}
</style>
