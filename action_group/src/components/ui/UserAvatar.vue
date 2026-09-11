<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{ name: string; color?: string; size?: number }>(),
  { color: '#6366f1', size: 36 },
)

const initials = computed(() => {
  const parts = props.name.trim().split(/\s+/).filter(Boolean)
  return parts
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join('')
})
</script>

<template>
  <span
    class="avatar"
    :style="{ background: color, width: size + 'px', height: size + 'px', fontSize: size * 0.4 + 'px' }"
  >
    {{ initials }}
  </span>
</template>

<style scoped>
.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-weight: 700;
  flex-shrink: 0;
}
</style>
