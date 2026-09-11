<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'
import { useDepartmentsStore } from '@/stores/departments'
import { usePlansStore } from '@/stores/plans'
import { useDirectionsStore } from '@/stores/directions'
import { usePermissions } from '@/composables/usePermissions'
import { directionBadgeVariant } from '@/utils/directionBadge'
import type { User } from '@/types'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseTabs from '@/components/ui/BaseTabs.vue'
import UserAvatar from '@/components/ui/UserAvatar.vue'
import ProgressBar from '@/components/ui/ProgressBar.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { Folder } from '@lucide/vue'

const users = useUsersStore()
const departments = useDepartmentsStore()
const plans = usePlansStore()
const directions = useDirectionsStore()
const perm = usePermissions()
const router = useRouter()
const route = useRoute()

onMounted(async () => {
  await Promise.all([users.fetchAll(), departments.fetchAll(), plans.fetchAll(), directions.fetchAll()])
  if (typeof route.query.dept === 'string') departmentFilter.value = route.query.dept
})

const search = ref('')
const directionFilter = ref('')
const departmentFilter = ref('')
const viewMode = ref<'list' | 'tree'>('list')

const visibleUsers = computed(() => users.items.filter((u) => perm.visibleEmployeeIds.value.has(u.id)))

const departmentOptions = computed(() => {
  const ids = new Set<string>()
  for (const u of visibleUsers.value) {
    if (!u.departmentId) continue
    ids.add(u.departmentId)
    departments.ancestorsOf(u.departmentId).forEach((a) => ids.add(a))
  }
  return departments.items
    .filter((d) => ids.has(d.id))
    .map((d) => ({ value: d.id, label: departments.pathLabel(d.id) }))
    .sort((a, b) => a.label.localeCompare(b.label))
})

function progressFor(userId: string): number {
  const mine = plans.forUser(userId)
  if (!mine.length) return 0
  return Math.round((mine.filter((p) => p.status === 'confirmed').length / mine.length) * 100)
}

function problemsFor(userId: string): number {
  return plans.forUser(userId).filter((p) => p.status === 'problem').length
}

function matchesFilters(u: User): boolean {
  if (directionFilter.value && u.directionId !== directionFilter.value) return false
  if (departmentFilter.value) {
    const chain = u.departmentId ? [u.departmentId, ...departments.ancestorsOf(u.departmentId)] : []
    if (!chain.includes(departmentFilter.value)) return false
  }
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    if (!u.fullName.toLowerCase().includes(q) && !u.login.toLowerCase().includes(q)) return false
  }
  return true
}

const filteredUsers = computed(() => visibleUsers.value.filter(matchesFilters))

interface TreeGroup {
  id: string
  label: string
  depth: number
  users: User[]
}

const treeGroups = computed<TreeGroup[]>(() => {
  const relevantDeptIds = new Set<string>()
  for (const u of filteredUsers.value) {
    if (!u.departmentId) continue
    relevantDeptIds.add(u.departmentId)
    departments.ancestorsOf(u.departmentId).forEach((a) => relevantDeptIds.add(a))
  }

  function depthOf(id: string): number {
    return departments.ancestorsOf(id).length
  }

  const groups: TreeGroup[] = [...relevantDeptIds]
    .map((id) => ({
      id,
      label: departments.byId.get(id)?.name ?? '—',
      depth: depthOf(id),
      users: filteredUsers.value.filter((u) => u.departmentId === id),
    }))
    .sort((a, b) => departments.pathLabel(a.id).localeCompare(departments.pathLabel(b.id)))

  return groups
})
</script>

<template>
  <div class="stack gap-lg">
    <div class="row gap-md" style="justify-content: space-between; flex-wrap: wrap">
      <h1 class="text-lg">Сотрудники</h1>
      <BaseTabs v-model="viewMode" :tabs="[{ value: 'list', label: 'Список' }, { value: 'tree', label: 'По подразделениям' }]" />
    </div>

    <BaseCard>
      <div class="filters">
        <BaseInput v-model="search" placeholder="Поиск по имени или логину" />
        <BaseSelect
          v-model="directionFilter"
          placeholder="Все направления"
          :options="directions.items.map((d) => ({ value: d.id, label: d.name }))"
        />
        <BaseSelect v-model="departmentFilter" placeholder="Все подразделения" :options="departmentOptions" />
      </div>
    </BaseCard>

    <EmptyState v-if="!filteredUsers.length" title="Никого не нашлось" description="Попробуйте изменить фильтры" />

    <div v-else-if="viewMode === 'list'" class="grid grid-cards">
      <BaseCard
        v-for="u in filteredUsers"
        :key="u.id"
        class="employee-card"
        @click="router.push({ name: 'employee-profile', params: { id: u.id } })"
      >
        <div class="row gap-sm">
          <UserAvatar :name="u.fullName" :color="u.avatarColor" :size="40" />
          <div style="min-width: 0; flex: 1">
            <p class="employee-card__name">{{ u.fullName }}</p>
            <p class="text-sm text-muted">{{ departments.pathLabel(u.departmentId) }}</p>
          </div>
          <BaseBadge :variant="directionBadgeVariant(u.directionId)">{{ directions.name(u.directionId) }}</BaseBadge>
        </div>
        <div class="stack gap-xs" style="margin-top: 14px">
          <div class="row" style="justify-content: space-between">
            <span class="text-sm text-muted">Прогресс плана</span>
            <span class="text-sm" style="font-weight: 700">{{ progressFor(u.id) }}%</span>
          </div>
          <ProgressBar :value="progressFor(u.id)" size="sm" />
        </div>
        <BaseBadge v-if="problemsFor(u.id) > 0" variant="danger" style="margin-top: 10px">
          {{ problemsFor(u.id) }} проблем{{ problemsFor(u.id) === 1 ? 'а' : '' }}
        </BaseBadge>
      </BaseCard>
    </div>

    <div v-else class="stack gap-md">
      <BaseCard v-for="group in treeGroups" :key="group.id" :padded="false">
        <div class="tree-group__header" :style="{ paddingLeft: 16 + group.depth * 18 + 'px' }">
          <Folder :size="16" class="text-faint" />
          <h3 class="text-lg" style="font-size: 15px">{{ group.label }}</h3>
          <span class="text-sm text-faint">{{ group.users.length }}</span>
        </div>
        <ul v-if="group.users.length" class="tree-group__list">
          <li
            v-for="u in group.users"
            :key="u.id"
            class="tree-group__item"
            @click="router.push({ name: 'employee-profile', params: { id: u.id } })"
          >
            <UserAvatar :name="u.fullName" :color="u.avatarColor" :size="30" />
            <span class="tree-group__name">{{ u.fullName }}</span>
            <BaseBadge :variant="directionBadgeVariant(u.directionId)">{{ directions.name(u.directionId) }}</BaseBadge>
            <span class="text-sm text-muted">{{ progressFor(u.id) }}%</span>
          </li>
        </ul>
      </BaseCard>
    </div>
  </div>
</template>

<style scoped>
.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.employee-card {
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.employee-card:hover {
  box-shadow: var(--shadow-md);
}

.employee-card__name {
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tree-group__header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
}

.tree-group__list {
  list-style: none;
  margin: 0;
  padding: 6px;
}

.tree-group__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: var(--radius-md);
  cursor: pointer;
}
.tree-group__item:hover {
  background: var(--color-surface-alt);
}

.tree-group__name {
  flex: 1;
  font-size: 13.5px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
