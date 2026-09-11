<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'
import { useDepartmentsStore } from '@/stores/departments'
import { usePlansStore } from '@/stores/plans'
import { useSkillsStore } from '@/stores/skills'
import { useDirectionsStore } from '@/stores/directions'
import { usePermissions } from '@/composables/usePermissions'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import UserAvatar from '@/components/ui/UserAvatar.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import VkNotificationsCard from '@/components/dashboard/VkNotificationsCard.vue'
import { ArrowRight } from '@lucide/vue'

const auth = useAuthStore()
const users = useUsersStore()
const departments = useDepartmentsStore()
const plans = usePlansStore()
const skills = useSkillsStore()
const directions = useDirectionsStore()
const perm = usePermissions()
const router = useRouter()

onMounted(async () => {
  await Promise.all([users.fetchAll(), departments.fetchAll(), plans.fetchAll(), skills.fetchAll(), directions.fetchAll()])
})

const me = computed(() => auth.currentUser)

const visibleIds = computed(() => perm.visibleEmployeeIds.value)
const teamIds = computed(() => perm.managedEmployeeIds.value)

const stats = computed(() => {
  const scopeIds = perm.isAdmin.value ? new Set(users.items.map((u) => u.id)) : teamIds.value
  const scopePlans = plans.items.filter((p) => scopeIds.has(p.userId))
  const confirmed = scopePlans.filter((p) => p.status === 'confirmed').length
  const problems = scopePlans.filter((p) => p.status === 'problem').length
  const total = scopePlans.length
  return {
    people: scopeIds.size,
    departments: departments.items.length,
    progress: total ? Math.round((confirmed / total) * 100) : 0,
    problems,
  }
})

const myPlanProgress = computed(() => {
  if (!me.value) return 0
  const mine = plans.items.filter((p) => p.userId === me.value!.id)
  if (!mine.length) return 0
  const confirmed = mine.filter((p) => p.status === 'confirmed').length
  return Math.round((confirmed / mine.length) * 100)
})

const upcoming = computed(() => {
  const now = Date.now()
  return plans.items
    .filter((p) => visibleIds.value.has(p.userId) && p.status !== 'confirmed')
    .map((p) => ({ ...p, daysLeft: Math.ceil((new Date(p.plannedDate).getTime() - now) / 86400000) }))
    .sort((a, b) => a.plannedDate.localeCompare(b.plannedDate))
    .slice(0, 6)
})

function skillName(id: string) {
  return skills.byId.get(id)?.name ?? '—'
}
function userName(id: string) {
  return users.byId.get(id)?.fullName ?? '—'
}
</script>

<template>
  <div class="stack gap-lg">
    <div>
      <h1 class="text-lg">Здравствуйте, {{ me?.fullName?.split(' ')[0] }}</h1>
      <p class="text-muted text-sm">
        {{ me ? directions.name(me.directionId) : '' }} · {{ departments.pathLabel(me?.departmentId ?? null) }}
      </p>
    </div>

    <div class="grid grid-cards">
      <BaseCard>
        <p class="text-sm text-muted">Мой прогресс по плану</p>
        <p class="stat">{{ myPlanProgress }}%</p>
        <BaseButton size="sm" variant="ghost" @click="me && router.push({ name: 'employee-profile', params: { id: me.id } })">
          Открыть мой профиль <ArrowRight :size="14" />
        </BaseButton>
      </BaseCard>

      <BaseCard v-if="perm.hasSubordinates.value || perm.isAdmin.value">
        <p class="text-sm text-muted">{{ perm.isAdmin.value ? 'Всего сотрудников' : 'В моей команде' }}</p>
        <p class="stat">{{ stats.people }}</p>
        <BaseButton size="sm" variant="ghost" @click="router.push('/employees')">Список сотрудников <ArrowRight :size="14" /></BaseButton>
      </BaseCard>

      <BaseCard v-if="perm.hasSubordinates.value || perm.isAdmin.value">
        <p class="text-sm text-muted">Выполнение плана обучения</p>
        <p class="stat">{{ stats.progress }}%</p>
        <BaseButton size="sm" variant="ghost" @click="router.push('/analytics')">Подробная аналитика <ArrowRight :size="14" /></BaseButton>
      </BaseCard>

      <BaseCard v-if="perm.hasSubordinates.value || perm.isAdmin.value">
        <p class="text-sm text-muted">Открытые проблемы</p>
        <p class="stat" :class="{ 'stat--danger': stats.problems > 0 }">{{ stats.problems }}</p>
        <span class="text-sm text-faint">по просроченным навыкам плана</span>
      </BaseCard>
    </div>

    <BaseCard :padded="false">
      <div class="section-header">
        <h2 class="text-lg">Ближайшие плановые даты</h2>
      </div>
      <div v-if="!upcoming.length" class="empty-inline text-muted text-sm">Нет запланированных подтверждений</div>
      <ul v-else class="upcoming-list">
        <li v-for="item in upcoming" :key="item.id" class="upcoming-item">
          <UserAvatar :name="userName(item.userId)" :size="30" />
          <div class="upcoming-item__body">
            <p class="upcoming-item__title">{{ skillName(item.skillId) }}</p>
            <p class="text-sm text-muted">{{ userName(item.userId) }}</p>
          </div>
          <BaseBadge :variant="item.status === 'problem' ? 'danger' : item.daysLeft <= 7 ? 'warning' : 'neutral'">
            {{ item.status === 'problem' ? 'просрочено' : `через ${item.daysLeft} дн.` }}
          </BaseBadge>
        </li>
      </ul>
    </BaseCard>

    <VkNotificationsCard />
  </div>
</template>

<style scoped>
.stat {
  font-size: 28px;
  font-weight: 800;
  margin: 6px 0 10px;
}
.stat--danger {
  color: var(--color-danger);
}

.section-header {
  padding: 16px 18px 0;
}

.empty-inline {
  padding: 24px 18px;
}

.upcoming-list {
  list-style: none;
  margin: 0;
  padding: 8px;
}

.upcoming-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: var(--radius-md);
}

.upcoming-item:hover {
  background: var(--color-surface-alt);
}

.upcoming-item__body {
  flex: 1;
  min-width: 0;
}

.upcoming-item__title {
  font-weight: 600;
  font-size: 14px;
}
</style>
