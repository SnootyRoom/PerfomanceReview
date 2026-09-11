<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '@/components/layout/AppShell.vue'
import ToastHost from '@/components/ui/ToastHost.vue'
import ConfirmHost from '@/components/ui/ConfirmHost.vue'

const route = useRoute()
const bare = computed(() => route.meta.public === true)
</script>

<template>
  <AppShell v-if="!bare" />
  <router-view v-else />
  <ToastHost />
  <ConfirmHost />
</template>
