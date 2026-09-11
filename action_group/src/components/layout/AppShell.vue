<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import BottomNav from './BottomNav.vue'
</script>

<template>
  <div class="shell">
    <AppHeader />
    <div class="shell__body">
      <AppSidebar class="shell__sidebar" />
      <main class="shell__main container">
        <router-view v-slot="{ Component, route }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </Transition>
        </router-view>
      </main>
    </div>
    <BottomNav class="shell__bottom-nav" />
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
}

.shell__body {
  display: flex;
}

.shell__sidebar {
  display: none;
}

.shell__main {
  flex: 1;
  min-width: 0;
  padding-block: 20px;
  padding-bottom: calc(var(--bottom-nav-height) + 24px);
}

.shell__bottom-nav {
  display: flex;
}

@media (min-width: 861px) {
  .shell__sidebar {
    display: block;
  }
  .shell__main {
    padding-block: 28px;
  }
  .shell__bottom-nav {
    display: none;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
