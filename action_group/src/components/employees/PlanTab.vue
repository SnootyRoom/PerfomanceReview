<script setup lang="ts">
import { computed, ref } from 'vue'
import { usePlansStore } from '@/stores/plans'
import { useSkillsStore } from '@/stores/skills'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import type { PlanItemStatus, User } from '@/types'
import { X } from '@lucide/vue'

const props = defineProps<{ employee: User; canManage: boolean }>()

const plans = usePlansStore()
const skills = useSkillsStore()
const { confirm } = useConfirm()
const toast = useToast()

const items = computed(() =>
  plans.forUser(props.employee.id).sort((a, b) => a.plannedDate.localeCompare(b.plannedDate)),
)

const statusMeta: Record<PlanItemStatus, { label: string; variant: 'success' | 'warning' | 'danger' }> = {
  confirmed: { label: 'Подтверждён', variant: 'success' },
  planned: { label: 'В плане', variant: 'warning' },
  problem: { label: 'Просрочен', variant: 'danger' },
}

const showAddModal = ref(false)
const newSkillId = ref('')
const newPlannedDate = ref('')
const saving = ref(false)

const availableSkills = computed(() => {
  const taken = new Set(items.value.map((p) => p.skillId))
  return skills.forDirection(props.employee.directionId).filter((s) => !taken.has(s.id))
})

function openAddModal() {
  newSkillId.value = ''
  newPlannedDate.value = new Date().toISOString().slice(0, 10)
  showAddModal.value = true
}

async function submitAdd() {
  if (!newSkillId.value || !newPlannedDate.value) return
  saving.value = true
  try {
    await plans.addSkill({ userId: props.employee.id, skillId: newSkillId.value, plannedDate: newPlannedDate.value })
    toast.success('Навык добавлен в план')
    showAddModal.value = false
  } catch (e) {
    toast.error(e instanceof Error ? e.message : 'Не удалось добавить навык')
  } finally {
    saving.value = false
  }
}

const editingId = ref<string | null>(null)
const editDate = ref('')

function startEdit(id: string, current: string) {
  editingId.value = id
  editDate.value = current
}

async function saveEdit(id: string) {
  await plans.updatePlannedDate(id, editDate.value)
  editingId.value = null
  toast.success('Дата обновлена')
}

async function removeItem(id: string, skillName: string) {
  const ok = await confirm(`Убрать «${skillName}» из плана обучения?`, { danger: true, confirmLabel: 'Убрать' })
  if (!ok) return
  await plans.remove(id)
  toast.success('Навык убран из плана')
}
</script>

<template>
  <div class="stack gap-md">
    <div class="row" style="justify-content: flex-end">
      <BaseButton v-if="canManage" size="sm" @click="openAddModal">+ Добавить навык в план</BaseButton>
    </div>

    <EmptyState v-if="!items.length" title="План обучения пуст" description="Добавьте навыки из справочника, чтобы начать планирование" />

    <BaseCard v-else :padded="false">
      <ul class="plan-list">
        <li v-for="item in items" :key="item.id" class="plan-item">
          <div class="plan-item__main">
            <p class="plan-item__name">{{ skills.name(item.skillId) }}</p>
            <p class="text-sm text-muted">
              Плановая дата:
              <template v-if="editingId === item.id">
                <input v-model="editDate" type="date" class="plan-item__date-input" />
                <button class="plan-item__link" type="button" @click="saveEdit(item.id)">сохранить</button>
                <button class="plan-item__link" type="button" @click="editingId = null">отмена</button>
              </template>
              <template v-else>
                {{ item.plannedDate }}
                <button v-if="canManage && item.status !== 'confirmed'" class="plan-item__link" type="button" @click="startEdit(item.id, item.plannedDate)">
                  изменить
                </button>
              </template>
              <template v-if="item.confirmedDate"> · подтверждён {{ item.confirmedDate }}</template>
            </p>
          </div>
          <BaseBadge :variant="statusMeta[item.status].variant">{{ statusMeta[item.status].label }}</BaseBadge>
          <button v-if="canManage" class="plan-item__remove" type="button" title="Убрать из плана" @click="removeItem(item.id, skills.name(item.skillId))">
            <X :size="14" />
          </button>
        </li>
      </ul>
    </BaseCard>

    <BaseModal v-if="showAddModal" title="Добавить навык в план" @close="showAddModal = false">
      <div class="stack gap-md">
        <BaseSelect
          v-model="newSkillId"
          label="Навык"
          required
          placeholder="Выберите навык"
          :options="availableSkills.map((s) => ({ value: s.id, label: s.name }))"
        />
        <BaseInput v-model="newPlannedDate" type="date" label="Плановая дата подтверждения" required />
      </div>
      <template #footer>
        <BaseButton variant="secondary" @click="showAddModal = false">Отмена</BaseButton>
        <BaseButton :loading="saving" :disabled="!newSkillId || !newPlannedDate" @click="submitAdd">Добавить</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.plan-list {
  list-style: none;
  margin: 0;
  padding: 6px;
}

.plan-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 10px;
  border-bottom: 1px solid var(--color-border);
}
.plan-item:last-child {
  border-bottom: none;
}

.plan-item__main {
  flex: 1;
  min-width: 0;
}

.plan-item__name {
  font-weight: 600;
  font-size: 14px;
}

.plan-item__link {
  border: none;
  background: none;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 12.5px;
  padding: 0 2px;
}

.plan-item__date-input {
  font-size: 12.5px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 1px 4px;
}

.plan-item__remove {
  border: none;
  background: none;
  color: var(--color-text-faint);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.plan-item__remove:hover {
  color: var(--color-danger);
}
</style>
