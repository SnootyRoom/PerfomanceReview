<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'
import { useDepartmentsStore } from '@/stores/departments'
import { usePlansStore } from '@/stores/plans'
import { useMeetingsStore } from '@/stores/meetings'
import { useSkillsStore } from '@/stores/skills'
import { usePermissions } from '@/composables/usePermissions'
import { useDirectionsStore } from '@/stores/directions'
import { directionBadgeVariant } from '@/utils/directionBadge'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseTabs from '@/components/ui/BaseTabs.vue'
import UserAvatar from '@/components/ui/UserAvatar.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { FileSpreadsheet, FileText, Lock } from '@lucide/vue'
import { useFileDownload } from '@/composables/useFileDownload'
import BaseButton from '@/components/ui/BaseButton.vue'
import PlanTab from '@/components/employees/PlanTab.vue'
import MeetingsTab from '@/components/employees/MeetingsTab.vue'
import ProblemsTab from '@/components/employees/ProblemsTab.vue'
import EmployeeAnalyticsTab from '@/components/employees/EmployeeAnalyticsTab.vue'

const props = defineProps<{ id: string }>()

const users = useUsersStore()
const departments = useDepartmentsStore()
const plans = usePlansStore()
const meetings = useMeetingsStore()
const skills = useSkillsStore()
const directions = useDirectionsStore()
const perm = usePermissions()
const router = useRouter()
const route = useRoute()

const ready = ref(false)

onMounted(async () => {
  await Promise.all([
    users.fetchAll(),
    departments.fetchAll(),
    plans.fetchAll(),
    meetings.fetchAll(),
    skills.fetchAll(),
    directions.fetchAll(),
  ])
  ready.value = true
})

const employee = computed(() => users.byId.get(props.id) ?? null)
const canView = computed(() => (employee.value ? perm.canView(employee.value.id) : false))
const canManage = computed(() => (employee.value ? perm.canManage(employee.value.id) : false))

const managerName = computed(() => {
  if (!employee.value?.departmentId) return null
  const chain = [employee.value.departmentId, ...departments.ancestorsOf(employee.value.departmentId)]
  for (const deptId of chain) {
    const managerId = departments.byId.get(deptId)?.managerId
    if (managerId && managerId !== employee.value.id) return users.fullName(managerId)
  }
  return null
})

const problemsCount = computed(() =>
  employee.value ? meetings.forUser(employee.value.id).flatMap((m) => m.problems).filter((p) => !p.resolved).length : 0,
)

const validTabs = ['plan', 'meetings', 'problems', 'analytics']
const initialTab = typeof route.query.tab === 'string' && validTabs.includes(route.query.tab) ? route.query.tab : 'plan'
const activeTab = ref(initialTab)

const { download } = useFileDownload()
function exportReport(format: 'xlsx' | 'pdf') {
  if (!employee.value) return
  download(`/export/employees/${employee.value.id}.${format}`, `report_${employee.value.login}.${format}`)
}
</script>

<template>
  <div v-if="!ready" class="text-muted">Загрузка…</div>

  <EmptyState v-else-if="!employee" title="Сотрудник не найден">
    <template #action>
      <BaseButton variant="secondary" @click="router.push('/employees')">К списку сотрудников</BaseButton>
    </template>
  </EmptyState>

  <EmptyState v-else-if="!canView" :icon="Lock" title="Нет доступа" description="У вас нет прав для просмотра профиля этого сотрудника" />

  <div v-else class="stack gap-lg">
    <BaseCard>
      <div class="profile-head">
        <UserAvatar :name="employee.fullName" :color="employee.avatarColor" :size="56" />
        <div class="profile-head__info">
          <h1 class="text-lg">{{ employee.fullName }}</h1>
          <p class="text-sm text-muted">{{ departments.pathLabel(employee.departmentId) }}</p>
          <p v-if="managerName" class="text-sm text-muted">Руководитель: {{ managerName }}</p>
        </div>
        <div class="profile-head__badges">
          <BaseBadge :variant="directionBadgeVariant(employee.directionId)">{{ directions.name(employee.directionId) }}</BaseBadge>
          <BaseBadge v-if="employee.isAdmin" variant="info">Администратор</BaseBadge>
          <BaseBadge v-if="problemsCount" variant="danger">{{ problemsCount }} открытых проблем</BaseBadge>
        </div>
        <div class="row gap-xs">
          <button type="button" class="export-btn" title="Экспорт в Excel" @click="exportReport('xlsx')">
            <FileSpreadsheet :size="16" />
          </button>
          <button type="button" class="export-btn" title="Экспорт в PDF" @click="exportReport('pdf')">
            <FileText :size="16" />
          </button>
        </div>
      </div>
    </BaseCard>

    <BaseTabs
      v-model="activeTab"
      :tabs="[
        { value: 'plan', label: 'План обучения' },
        { value: 'meetings', label: 'Встречи' },
        { value: 'problems', label: 'Проблемы', count: problemsCount || undefined },
        { value: 'analytics', label: 'Аналитика' },
      ]"
    />

    <PlanTab v-if="activeTab === 'plan'" :employee="employee" :can-manage="canManage" />
    <MeetingsTab v-else-if="activeTab === 'meetings'" :employee="employee" :can-manage="canManage" />
    <ProblemsTab v-else-if="activeTab === 'problems'" :employee="employee" :can-manage="canManage" />
    <EmployeeAnalyticsTab v-else :employee="employee" />
  </div>
</template>

<style scoped>
.profile-head {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.profile-head__info {
  flex: 1;
  min-width: 160px;
}

.profile-head__badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.export-btn {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-muted);
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.export-btn:hover {
  background: var(--color-surface-alt);
  color: var(--color-text);
}
</style>
