<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMeetingsStore } from '@/stores/meetings'
import { useScheduledMeetingsStore } from '@/stores/scheduledMeetings'
import { useUsersStore } from '@/stores/users'
import { useSkillsStore } from '@/stores/skills'
import { renderMarkdown } from '@/composables/useMarkdown'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'
import type { User } from '@/types'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseTextarea from '@/components/ui/BaseTextarea.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { Calendar, Check, ChevronDown, ChevronUp, Link2, Paperclip, X } from '@lucide/vue'

const props = defineProps<{ employee: User; canManage: boolean }>()

const meetings = useMeetingsStore()
const scheduled = useScheduledMeetingsStore()
const users = useUsersStore()
const skills = useSkillsStore()
const router = useRouter()
const { confirm } = useConfirm()
const toast = useToast()

onMounted(() => scheduled.fetchAll())

const list = computed(() => meetings.forUser(props.employee.id))
const upcoming = computed(() => scheduled.forUser(props.employee.id))
const expanded = ref<Set<string>>(new Set())

function toggle(id: string) {
  const next = new Set(expanded.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  expanded.value = next
}

function goCreate() {
  router.push({ name: 'meeting-new', params: { id: props.employee.id } })
}

const showScheduleModal = ref(false)
const scheduleDate = ref(new Date().toISOString().slice(0, 10))
const scheduleNote = ref('')
const scheduling = ref(false)

function openScheduleModal() {
  scheduleDate.value = new Date().toISOString().slice(0, 10)
  scheduleNote.value = ''
  showScheduleModal.value = true
}

async function submitSchedule() {
  scheduling.value = true
  try {
    await scheduled.create({ employeeId: props.employee.id, scheduledDate: scheduleDate.value, note: scheduleNote.value.trim() })
    toast.success('Встреча запланирована')
    showScheduleModal.value = false
  } catch (e) {
    toast.error(e instanceof Error ? e.message : 'Не удалось запланировать встречу')
  } finally {
    scheduling.value = false
  }
}

async function cancelScheduled(id: string) {
  const ok = await confirm('Отменить запланированную встречу?', { danger: true, confirmLabel: 'Отменить' })
  if (!ok) return
  await scheduled.remove(id)
  toast.success('Встреча отменена')
}
</script>

<template>
  <div class="stack gap-md">
    <div class="row gap-sm" style="justify-content: flex-end">
      <BaseButton v-if="canManage" size="sm" variant="secondary" @click="openScheduleModal">
        <Calendar :size="14" /> Запланировать
      </BaseButton>
      <BaseButton v-if="canManage" size="sm" @click="goCreate">+ Провести встречу (PR)</BaseButton>
    </div>

    <BaseCard v-if="upcoming.length" :padded="false">
      <div class="section-header">
        <p class="text-sm text-muted" style="font-weight: 700">Предстоящие встречи</p>
      </div>
      <ul class="upcoming-list">
        <li v-for="s in upcoming" :key="s.id">
          <div class="upcoming-item__body">
            <p class="upcoming-item__date">{{ s.scheduledDate }}</p>
            <p v-if="s.note" class="text-sm text-muted">{{ s.note }}</p>
            <p class="text-sm text-faint">запланировал(а) {{ users.fullName(s.conductedById) }}</p>
          </div>
          <button v-if="canManage" type="button" class="upcoming-item__cancel" title="Отменить" @click="cancelScheduled(s.id)">
            <X :size="14" />
          </button>
        </li>
      </ul>
    </BaseCard>

    <EmptyState v-if="!list.length" title="Встреч пока не было" description="Здесь появится история протоколов PR-встреч" />

    <BaseCard v-for="m in list" :key="m.id" :padded="false" class="meeting">
      <button class="meeting__head" type="button" @click="toggle(m.id)">
        <div>
          <p class="meeting__date">{{ m.date }}</p>
          <p class="text-sm text-muted">Провёл(а): {{ users.fullName(m.conductedById) }}</p>
        </div>
        <div class="row gap-sm">
          <BaseBadge v-if="m.skillMarks.some((s) => s.confirmed)" variant="success">
            {{ m.skillMarks.filter((s) => s.confirmed).length }} навык(ов) подтверждено
          </BaseBadge>
          <BaseBadge v-if="m.problems.some((p) => !p.resolved)" variant="danger">проблема</BaseBadge>
          <ChevronUp v-if="expanded.has(m.id)" :size="15" class="meeting__chevron" />
          <ChevronDown v-else :size="15" class="meeting__chevron" />
        </div>
      </button>

      <div v-if="expanded.has(m.id)" class="meeting__body">
        <div class="markdown-body" v-html="renderMarkdown(m.summaryMarkdown)" />

        <div v-if="m.skillMarks.length" class="meeting__section">
          <p class="meeting__section-title">Отметки по навыкам</p>
          <ul class="meeting__marks">
            <li v-for="mark in m.skillMarks" :key="mark.skillId">
              <BaseBadge :variant="mark.confirmed ? 'success' : 'neutral'">
                <Check v-if="mark.confirmed" :size="12" />
                {{ skills.name(mark.skillId) }}
              </BaseBadge>
              <span v-if="mark.comment" class="text-sm text-muted"> — {{ mark.comment }}</span>
            </li>
          </ul>
        </div>

        <div v-if="m.attachments.length" class="meeting__section">
          <p class="meeting__section-title">Материалы</p>
          <ul class="meeting__attachments">
            <li v-for="a in m.attachments" :key="a.id">
              <a :href="a.url" target="_blank" rel="noopener" class="meeting__attachment-link">
                <Link2 v-if="a.type === 'link'" :size="13" />
                <Paperclip v-else :size="13" />
                {{ a.name }}
              </a>
            </li>
          </ul>
        </div>

        <div v-if="m.problems.length" class="meeting__section">
          <p class="meeting__section-title">Отмеченные проблемы</p>
          <ul class="meeting__problems">
            <li v-for="p in m.problems" :key="p.id" :class="{ 'is-resolved': p.resolved }">
              <BaseBadge :variant="p.resolved ? 'neutral' : 'danger'">
                {{ p.scope === 'skill' ? skills.name(p.skillId ?? '') : 'Общее' }}
              </BaseBadge>
              {{ p.comment }}
            </li>
          </ul>
        </div>
      </div>
    </BaseCard>

    <BaseModal v-if="showScheduleModal" title="Запланировать встречу" @close="showScheduleModal = false">
      <div class="stack gap-md">
        <BaseInput v-model="scheduleDate" type="date" label="Дата встречи" required />
        <BaseTextarea v-model="scheduleNote" label="Заметка (необязательно)" :rows="3" placeholder="О чём поговорить" />
      </div>
      <template #footer>
        <BaseButton variant="secondary" @click="showScheduleModal = false">Отмена</BaseButton>
        <BaseButton :loading="scheduling" @click="submitSchedule">Запланировать</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.meeting__head {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border: none;
  background: none;
  cursor: pointer;
  text-align: left;
}

.meeting__date {
  font-weight: 700;
}

.meeting__chevron {
  color: var(--color-text-faint);
  flex-shrink: 0;
}

.meeting__body {
  padding: 0 16px 16px;
  border-top: 1px solid var(--color-border);
}

.meeting__section {
  margin-top: 14px;
}

.meeting__section-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-text-faint);
  margin-bottom: 8px;
}

.meeting__marks,
.meeting__attachments,
.meeting__problems {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13.5px;
}

.meeting__problems li.is-resolved {
  opacity: 0.55;
  text-decoration: line-through;
}

.meeting__attachment-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  font-size: 13.5px;
}

.section-header {
  padding: 14px 16px 0;
}

.upcoming-list {
  list-style: none;
  margin: 0;
  padding: 6px;
}

.upcoming-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: var(--radius-md);
}

.upcoming-list li:hover {
  background: var(--color-surface-alt);
}

.upcoming-item__body {
  flex: 1;
  min-width: 0;
}

.upcoming-item__date {
  font-weight: 700;
  font-size: 14px;
}

.upcoming-item__cancel {
  border: none;
  background: var(--color-surface-alt);
  color: var(--color-text-faint);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.upcoming-item__cancel:hover {
  color: var(--color-danger);
}
</style>
