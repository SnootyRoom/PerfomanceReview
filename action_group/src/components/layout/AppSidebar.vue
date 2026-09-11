<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { primaryNav, adminNav } from './navItems'

const auth = useAuthStore()
</script>

<template>
  <aside class="sidebar">
    <nav class="sidebar__nav">
      <router-link v-for="item in primaryNav" :key="item.to" :to="item.to" class="sidebar__item" active-class="sidebar__item--active">
        <component :is="item.icon" :size="17" class="sidebar__icon" />
        {{ item.label }}
      </router-link>

      <template v-if="auth.isAdmin">
        <p class="sidebar__group-label">Администрирование</p>
        <router-link v-for="item in adminNav" :key="item.to" :to="item.to" class="sidebar__item" active-class="sidebar__item--active">
          <component :is="item.icon" :size="17" class="sidebar__icon" />
          {{ item.label }}
        </router-link>
      </template>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  flex-shrink: 0;
  border-right: 1px solid var(--color-border);
  padding: 20px 12px;
  position: sticky;
  top: var(--header-height);
  height: calc(100vh - var(--header-height));
  overflow-y: auto;
}

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--color-text-muted);
  font-size: 14px;
  font-weight: 600;
}

.sidebar__item:hover {
  background: var(--color-surface-alt);
  color: var(--color-text);
}

.sidebar__item--active {
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.sidebar__icon {
  flex-shrink: 0;
}

.sidebar__group-label {
  margin: 18px 12px 6px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-faint);
  font-weight: 700;
}
</style>
