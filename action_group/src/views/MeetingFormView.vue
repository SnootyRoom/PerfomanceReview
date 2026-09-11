<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'
import { useSkillsStore } from '@/stores/skills'
import { useMeetingsStore } from '@/stores/meetings'
import { usePlansStore } from '@/stores/plans'
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/composables/usePermissions'
import { useToast } from '@/composables/useToast'
import { renderMarkdown } from '@/composables/useMarkdown'
import type { AttachmentType } from '@/types'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseTextarea from '@/components/ui/BaseTextarea.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import UserAvatar from '@/components/ui/UserAvatar.vue'
import { Lock, X } from '@lucide/vue'

const props = defineProps<{ id: string }>()

const users = useUsersStore()
const skills = useSkillsStore()
const meetings = useMeetingsStore()
const plans = usePlansStore()
const auth = useAuthStore()
const perm = usePermissions()
const toast = useToast()
const router = useRouter()

const ready = ref(false)

onMounted(async () => {
  await Promise.all([users.fetchAll(), skills.fetchAll(), plans.fetchAll()])
  ready.value = true
})

const employee = computed(() => users.byId.get(props.id) ?? null)
const allowed = computed(() => (employee.value ? perm.canManage(employee.value.id) : false))

const date = ref(new Date().toISOString().slice(0, 10))
const summary = ref('')
const showPreview = ref(false)
const submitting = ref(false)

interface AttachmentRow {
  type: AttachmentType
  name: string
  url: string
}
const attachments = reactive<AttachmentRow[]>([])

function addAttachmentLink() {
  attachments.push({ type: 'link', name: '', url: '' })
}

function onFileChosen(row: AttachmentRow, e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  row.name = file.name
  row.url = URL.createObjectURL(file)
}

function addAttachmentFile() {
  attachments.push({ type: 'file', name: '', url: '' })
}

function removeAttachment(idx: number) {
  attachments.splice(idx, 1)
}

interface SkillMarkRow {
  skillId: string
  confirmed: boolean
  comment: string
}
const skillMarks = reactive<SkillMarkRow[]>([])

const employeeSkillOptions = computed(() => {
  if (!employee.value) return []
  const used = new Set(skillMarks.map((m) => m.skillId))
  return skills.forDirection(employee.value.directionId).filter((s) => !used.has(s.id))
})

function addSkillMark() {
  const first = employeeSkillOptions.value[0]
  if (!first) return
  skillMarks.push({ skillId: first.id, confirmed: true, comment: '' })
}

function removeSkillMark(idx: number) {
  skillMarks.splice(idx, 1)
}

interface ProblemRow {
  scope: 'employee' | 'skill'
  skillId: string
  comment: string
}
const problems = reactive<ProblemRow[]>([])

function addProblem() {
  problems.push({ scope: 'employee', skillId: '', comment: '' })
}
function removeProblem(idx: number) {
  problems.splice(idx, 1)
}

const canSubmit = computed(() => date.value && summary.value.trim().length > 0)

async function submit() {
  if (!employee.value || !auth.currentUser || !canSubmit.value) return
  submitting.value = true
  try {
    await meetings.create({
      employeeId: employee.value.id,
      date: date.value,
      summaryMarkdown: summary.value.trim(),
      attachments: attachments
        .filter((a) => a.name.trim() && a.url.trim())
        .map((a) => ({ type: a.type, name: a.name.trim(), url: a.url.trim() })),
      skillMarks: skillMarks.map((m) => ({ skillId: m.skillId, confirmed: m.confirmed, comment: m.comment.trim() })),
      problems: problems
        .filter((p) => p.comment.trim() && (p.scope === 'employee' || p.skillId))
        .map((p) => ({ scope: p.scope, skillId: p.scope === 'skill' ? p.skillId : null, comment: p.comment.trim(), resolved: false })),
    })
    await plans.fetchAll(true)
    toast.success('Протокол встречи сохранён')
    router.push({ name: 'employee-profile', params: { id: employee.value.id }, query: { tab: 'meetings' } })
  } catch (e) {
    toast.error(e instanceof Error ? e.message : 'Не удалось сохранить встречу')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div v-if="!ready" class="text-muted">Загрузка…</div>
  <EmptyState v-else-if="!employee" title="Сотрудник не найден" />
  <EmptyState v-else-if="!allowed" :icon="Lock" title="Нет доступа" description="Проводить встречу может только руководитель этого сотрудника" />

  <form v-else class="stack gap-lg" @submit.prevent="submit">
    <div class="row gap-sm">
      <UserAvatar :name="employee.fullName" :color="employee.avatarColor" :size="40" />
      <div>
        <h1 class="text-lg">Протокол встречи · {{ employee.fullName }}</h1>
        <p class="text-sm text-muted">Проводит: {{ auth.currentUser?.fullName }}</p>
      </div>
    </div>

    <BaseCard class="stack gap-md">
      <BaseInput v-model="date" type="date" label="Дата встречи" required />

      <div class="stack gap-xs">
        <div class="row" style="justify-content: space-between">
          <span class="field__label">Итоги встречи (Markdown)</span>
          <button type="button" class="link-btn" @click="showPreview = !showPreview">
            {{ showPreview ? 'Редактировать' : 'Предпросмотр' }}
          </button>
        </div>
        <div v-if="showPreview" class="markdown-body preview-box" v-html="renderMarkdown(summary)" />
        <BaseTextarea v-else v-model="summary" :rows="7" placeholder="### Что обсудили&#10;- пункт 1&#10;- пункт 2" />
      </div>
    </BaseCard>

    <BaseCard class="stack gap-md">
      <div class="row" style="justify-content: space-between">
        <p style="font-weight: 700">Отметки по навыкам</p>
        <BaseButton size="sm" variant="secondary" type="button" :disabled="!employeeSkillOptions.length" @click="addSkillMark">
          + Добавить навык
        </BaseButton>
      </div>
      <p v-if="!skillMarks.length" class="text-sm text-muted">Навыки не отмечены</p>
      <div v-for="(row, idx) in skillMarks" :key="idx" class="mark-row">
        <BaseSelect
          v-model="row.skillId"
          :options="[
            { value: row.skillId, label: skills.name(row.skillId) },
            ...employeeSkillOptions.map((s) => ({ value: s.id, label: s.name })),
          ]"
        />
        <label class="mark-row__confirm">
          <input v-model="row.confirmed" type="checkbox" />
          Подтверждён
        </label>
        <BaseInput v-model="row.comment" placeholder="Комментарий (необязательно)" />
        <button type="button" class="remove-btn" @click="removeSkillMark(idx)"><X :size="14" /></button>
      </div>
    </BaseCard>

    <BaseCard class="stack gap-md">
      <div class="row" style="justify-content: space-between">
        <p style="font-weight: 700">Материалы</p>
        <div class="row gap-sm">
          <BaseButton size="sm" variant="secondary" type="button" @click="addAttachmentLink">+ Ссылка</BaseButton>
          <BaseButton size="sm" variant="secondary" type="button" @click="addAttachmentFile">+ Файл</BaseButton>
        </div>
      </div>
      <p v-if="!attachments.length" class="text-sm text-muted">Материалы не прикреплены</p>
      <div v-for="(row, idx) in attachments" :key="idx" class="attach-row">
        <BaseInput v-model="row.name" placeholder="Название" />
        <BaseInput v-if="row.type === 'link'" v-model="row.url" placeholder="https://…" />
        <input v-else type="file" class="file-input" @change="onFileChosen(row, $event)" />
        <button type="button" class="remove-btn" @click="removeAttachment(idx)"><X :size="14" /></button>
      </div>
    </BaseCard>

    <BaseCard class="stack gap-md">
      <div class="row" style="justify-content: space-between">
        <p style="font-weight: 700">Проблемы</p>
        <BaseButton size="sm" variant="secondary" type="button" @click="addProblem">+ Отметить проблему</BaseButton>
      </div>
      <p v-if="!problems.length" class="text-sm text-muted">Проблем не выявлено</p>
      <div v-for="(row, idx) in problems" :key="idx" class="problem-row">
        <BaseSelect
          v-model="row.scope"
          :options="[
            { value: 'employee', label: 'Общая проблема' },
            { value: 'skill', label: 'По конкретному навыку' },
          ]"
        />
        <BaseSelect
          v-if="row.scope === 'skill'"
          v-model="row.skillId"
          placeholder="Навык"
          :options="skillMarks.map((m) => ({ value: m.skillId, label: skills.name(m.skillId) }))"
        />
        <BaseInput v-model="row.comment" placeholder="Комментарий" />
        <button type="button" class="remove-btn" @click="removeProblem(idx)"><X :size="14" /></button>
      </div>
    </BaseCard>

    <div class="row gap-sm" style="justify-content: flex-end">
      <BaseButton variant="secondary" type="button" @click="router.back()">Отмена</BaseButton>
      <BaseButton type="submit" :loading="submitting" :disabled="!canSubmit">Сохранить протокол</BaseButton>
    </div>
  </form>
</template>

<style scoped>
.field__label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-muted);
}

.link-btn {
  border: none;
  background: none;
  color: var(--color-primary);
  font-size: 13px;
  cursor: pointer;
}

.preview-box {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 12px;
  min-height: 140px;
}

.mark-row,
.attach-row,
.problem-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
}

.mark-row {
  grid-template-columns: 1fr auto 1fr auto;
}

.mark-row__confirm {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  white-space: nowrap;
}

.attach-row,
.problem-row {
  grid-template-columns: 1fr 1fr auto;
}

.file-input {
  font-size: 13px;
}

.remove-btn {
  border: none;
  background: var(--color-surface-alt);
  color: var(--color-text-faint);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.remove-btn:hover {
  color: var(--color-danger);
}

@media (max-width: 640px) {
  .mark-row,
  .attach-row,
  .problem-row {
    grid-template-columns: 1fr;
  }
  .remove-btn {
    justify-self: end;
  }
}
</style>
