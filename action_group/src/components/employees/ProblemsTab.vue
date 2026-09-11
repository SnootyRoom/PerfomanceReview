<script setup lang="ts">
import { computed } from 'vue'
import { useMeetingsStore } from '@/stores/meetings'
import { useSkillsStore } from '@/stores/skills'
import { useToast } from '@/composables/useToast'
import type { User } from '@/types'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { CheckCircle2 } from '@lucide/vue'

const props = defineProps<{ employee: User; canManage: boolean }>()

const meetings = useMeetingsStore()
const skills = useSkillsStore()
const toast = useToast()

const rows = computed(() => {
  const result: { meetingId: string; date: string; problemId: string; scope: string; skillId: string | null; comment: string; resolved: boolean }[] = []
  for (const m of meetings.forUser(props.employee.id)) {
    for (const p of m.problems) {
      result.push({ meetingId: m.id, date: m.date, problemId: p.id, scope: p.scope, skillId: p.skillId, comment: p.comment, resolved: p.resolved })
    }
  }
  return result.sort((a, b) => Number(a.resolved) - Number(b.resolved) || b.date.localeCompare(a.date))
})

async function toggleResolved(row: (typeof rows.value)[number]) {
  await meetings.setProblemResolved(row.meetingId, row.problemId, !row.resolved)
  toast.success(row.resolved ? 'Проблема снова открыта' : 'Проблема отмечена как решённая')
}
</script>

<template>
  <div class="stack gap-md">
    <EmptyState v-if="!rows.length" :icon="CheckCircle2" title="Проблем не зафиксировано" />
    <BaseCard v-else :padded="false">
      <ul class="problems-list">
        <li v-for="row in rows" :key="row.problemId" :class="{ 'is-resolved': row.resolved }">
          <div class="problems-list__main">
            <BaseBadge :variant="row.resolved ? 'neutral' : 'danger'">
              {{ row.scope === 'skill' ? skills.name(row.skillId ?? '') : 'Общая проблема' }}
            </BaseBadge>
            <p class="text-sm" style="margin-top: 6px">{{ row.comment }}</p>
            <p class="text-sm text-faint">с встречи от {{ row.date }}</p>
          </div>
          <BaseButton v-if="canManage" size="sm" variant="secondary" @click="toggleResolved(row)">
            {{ row.resolved ? 'Открыть снова' : 'Отметить решённой' }}
          </BaseButton>
        </li>
      </ul>
    </BaseCard>
  </div>
</template>

<style scoped>
.problems-list {
  list-style: none;
  margin: 0;
  padding: 6px;
}
.problems-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 12px;
  border-bottom: 1px solid var(--color-border);
}
.problems-list li:last-child {
  border-bottom: none;
}
.problems-list li.is-resolved {
  opacity: 0.6;
}
</style>
