<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'
import { useDepartmentsStore } from '@/stores/departments'
import { usePlansStore } from '@/stores/plans'
import { useMeetingsStore } from '@/stores/meetings'
import { useScheduledMeetingsStore } from '@/stores/scheduledMeetings'
import { usePermissions } from '@/composables/usePermissions'
import BaseCard from '@/components/ui/BaseCard.vue'
import BarRow from '@/components/charts/BarRow.vue'
import DonutProgress from '@/components/charts/DonutProgress.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import UserAvatar from '@/components/ui/UserAvatar.vue'
import AiAnalysisModal from '@/components/ui/AiAnalysisModal.vue'
import { FileSpreadsheet, FileText, Sparkles } from '@lucide/vue'
import { useFileDownload } from '@/composables/useFileDownload'
import { http } from '@/api/http'

const users = useUsersStore()
const departments = useDepartmentsStore()
const plans = usePlansStore()
const meetings = useMeetingsStore()
const scheduled = useScheduledMeetingsStore()
const perm = usePermissions()
const router = useRouter()

onMounted(async () => {
  await Promise.all([
    users.fetchAll(),
    departments.fetchAll(),
    plans.fetchAll(),
    meetings.fetchAll(),
    scheduled.fetchAll(),
  ])
})

const upcomingMeetings = computed(() => {
  const scopeIds = perm.isAdmin.value ? new Set(users.items.map((u) => u.id)) : perm.visibleEmployeeIds.value
  return scheduled.items
    .filter((m) => scopeIds.has(m.employeeId))
    .slice()
    .sort((a, b) => a.scheduledDate.localeCompare(b.scheduledDate))
    .slice(0, 8)
})

const scopeDeptIds = computed(() =>
  perm.isAdmin.value ? new Set(departments.items.map((d) => d.id)) : perm.managedDepartmentIds.value,
)

function usersInSubtree(deptId: string): string[] {
  const ids = new Set([deptId, ...departments.descendantsOf(deptId)])
  return users.items.filter((u) => u.departmentId && ids.has(u.departmentId)).map((u) => u.id)
}

interface DeptStat {
  id: string
  label: string
  people: number
  completion: number
  openProblems: number
  planTotal: number
}

const deptStats = computed<DeptStat[]>(() => {
  return [...scopeDeptIds.value]
    .map((deptId) => {
      const memberIds = new Set(usersInSubtree(deptId))
      const relevantPlans = plans.items.filter((p) => memberIds.has(p.userId))
      const confirmed = relevantPlans.filter((p) => p.status === 'confirmed').length
      const openProblems = meetings.items
        .filter((m) => memberIds.has(m.employeeId))
        .flatMap((m) => m.problems)
        .filter((p) => !p.resolved).length
      return {
        id: deptId,
        label: departments.pathLabel(deptId),
        people: memberIds.size,
        completion: relevantPlans.length ? Math.round((confirmed / relevantPlans.length) * 100) : 0,
        openProblems,
        planTotal: relevantPlans.length,
      }
    })
    .filter((s) => s.people > 0)
    .sort((a, b) => a.label.localeCompare(b.label))
})

const overall = computed(() => {
  const scopeIds = perm.isAdmin.value ? new Set(users.items.map((u) => u.id)) : perm.visibleEmployeeIds.value
  const relevantPlans = plans.items.filter((p) => scopeIds.has(p.userId))
  const confirmed = relevantPlans.filter((p) => p.status === 'confirmed').length
  const openProblems = meetings.items
    .filter((m) => scopeIds.has(m.employeeId))
    .flatMap((m) => m.problems)
    .filter((p) => !p.resolved).length
  return {
    people: scopeIds.size,
    completion: relevantPlans.length ? Math.round((confirmed / relevantPlans.length) * 100) : 0,
    openProblems,
  }
})

function openDept(deptId: string) {
  router.push({ path: '/employees', query: { dept: deptId } })
}

const { download } = useFileDownload()
function exportDept(deptId: string, format: 'xlsx' | 'pdf') {
  download(`/export/departments/${deptId}.${format}`, `report_department.${format}`)
}

const aiShow = ref(false)
const aiLoading = ref(false)
const aiError = ref('')
const aiText = ref('')

async function openDeptAnalysis(deptId: string) {
  aiShow.value = true
  aiLoading.value = true
  aiError.value = ''
  aiText.value = ''
  try {
    const { data } = await http.post<{ text: string }>(`/ai/departments/${deptId}`)
    aiText.value = data.text
  } catch (e) {
    aiError.value = e instanceof Error ? e.message : 'Не удалось получить анализ'
  } finally {
    aiLoading.value = false
  }
}
</script>

<template>
  <div class="stack gap-lg">
    <div>
      <h1 class="text-lg">Аналитика</h1>
      <p class="text-sm text-muted">Прогресс обучения и открытые проблемы в разрезе подразделений</p>
    </div>

    <div class="grid" style="grid-template-columns: auto 1fr; align-items: center; gap: 24px">
      <BaseCard class="row" style="justify-content: center">
        <DonutProgress :value="overall.completion" />
      </BaseCard>
      <BaseCard>
        <p class="text-sm text-muted">Сотрудников в зоне видимости</p>
        <p class="stat">{{ overall.people }}</p>
        <p class="text-sm" :class="overall.openProblems ? 'text-danger' : 'text-muted'">
          {{ overall.openProblems }} открытых проблем
        </p>
      </BaseCard>
    </div>

    <BaseCard v-if="upcomingMeetings.length" :padded="false">
      <p style="font-weight: 700; padding: 16px 16px 0">Ближайшие встречи по команде</p>
      <ul class="upcoming-meetings">
        <li v-for="m in upcomingMeetings" :key="m.id" @click="router.push({ name: 'employee-profile', params: { id: m.employeeId }, query: { tab: 'meetings' } })">
          <UserAvatar :name="users.fullName(m.employeeId)" :size="30" />
          <div style="flex: 1; min-width: 0">
            <p class="text-sm" style="font-weight: 600">{{ users.fullName(m.employeeId) }}</p>
            <p v-if="m.note" class="text-sm text-muted">{{ m.note }}</p>
          </div>
          <span class="text-sm text-muted">{{ m.scheduledDate }}</span>
        </li>
      </ul>
    </BaseCard>

    <EmptyState v-if="!deptStats.length" title="Нет данных для отображения" description="Аналитика появится, когда в подразделениях будут сотрудники" />

    <BaseCard v-else>
      <p style="font-weight: 700; margin-bottom: 16px">По подразделениям</p>
      <div class="stack gap-md">
        <div v-for="d in deptStats" :key="d.id" class="dept-row">
          <button type="button" class="dept-row__main" @click="openDept(d.id)">
            <BarRow
              :label="d.label"
              :value="d.completion"
              :sub="`${d.people} сотр. · ${d.planTotal} навыков в планах`"
              :color="d.completion >= 70 ? 'var(--color-success)' : d.completion >= 40 ? 'var(--color-warning)' : 'var(--color-danger)'"
            />
          </button>
          <span v-if="d.openProblems" class="dept-row__problems">{{ d.openProblems }} проблем</span>
          <div class="row gap-xs">
            <button type="button" class="export-btn" title="Экспорт в Excel" @click="exportDept(d.id, 'xlsx')">
              <FileSpreadsheet :size="15" />
            </button>
            <button type="button" class="export-btn" title="Экспорт в PDF" @click="exportDept(d.id, 'pdf')">
              <FileText :size="15" />
            </button>
            <button type="button" class="export-btn" title="AI-анализ команды" @click="openDeptAnalysis(d.id)">
              <Sparkles :size="15" />
            </button>
          </div>
        </div>
      </div>
    </BaseCard>

    <AiAnalysisModal v-if="aiShow" :loading="aiLoading" :error="aiError" :text="aiText" @close="aiShow = false" />
  </div>
</template>

<style scoped>
.stat {
  font-size: 26px;
  font-weight: 800;
  margin: 4px 0;
}
.text-danger {
  color: var(--color-danger);
}

.dept-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: var(--radius-md);
}
.dept-row:hover {
  background: var(--color-surface-alt);
}

.dept-row__main {
  flex: 1;
  min-width: 0;
  border: none;
  background: none;
  padding: 0;
  cursor: pointer;
  text-align: left;
}

.export-btn {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-muted);
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
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

.dept-row__problems {
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-danger);
  background: var(--color-danger-soft);
  padding: 3px 10px;
  border-radius: 999px;
}

@media (max-width: 560px) {
  .grid {
    grid-template-columns: 1fr !important;
  }
}

.upcoming-meetings {
  list-style: none;
  margin: 0;
  padding: 8px;
}
.upcoming-meetings li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 8px;
  border-radius: var(--radius-md);
  cursor: pointer;
}
.upcoming-meetings li:hover {
  background: var(--color-surface-alt);
}
</style>
