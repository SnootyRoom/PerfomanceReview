<script setup lang="ts">
import { computed } from 'vue'
import { usePlansStore } from '@/stores/plans'
import { useMeetingsStore } from '@/stores/meetings'
import { computeAchievements } from '@/composables/useAchievements'
import BaseCard from '@/components/ui/BaseCard.vue'
import type { User } from '@/types'

const props = defineProps<{ employee: User }>()

const plans = usePlansStore()
const meetings = useMeetingsStore()

const achievements = computed(() => computeAchievements(plans.forUser(props.employee.id), meetings.forUser(props.employee.id)))
const earnedCount = computed(() => achievements.value.filter((a) => a.earned).length)
</script>

<template>
  <BaseCard>
    <div class="row" style="justify-content: space-between; margin-bottom: 14px">
      <p style="font-weight: 700">Достижения</p>
      <span class="text-sm text-muted">{{ earnedCount }} / {{ achievements.length }}</span>
    </div>
    <div class="badges-grid">
      <div v-for="a in achievements" :key="a.id" class="badge-tile" :class="{ 'badge-tile--earned': a.earned }" :title="a.description">
        <component :is="a.icon" :size="20" class="badge-tile__icon" />
        <span class="badge-tile__label">{{ a.label }}</span>
      </div>
    </div>
  </BaseCard>
</template>

<style scoped>
.badges-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}

.badge-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 6px;
  padding: 14px 8px;
  border-radius: var(--radius-md);
  background: var(--color-surface-alt);
  color: var(--color-text-faint);
  opacity: 0.55;
}

.badge-tile--earned {
  opacity: 1;
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.badge-tile__label {
  font-size: 11.5px;
  font-weight: 600;
  line-height: 1.25;
}
</style>
