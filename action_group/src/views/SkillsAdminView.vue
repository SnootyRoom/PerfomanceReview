<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useSkillsStore } from '@/stores/skills'
import { useDirectionsStore } from '@/stores/directions'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { directionBadgeVariant } from '@/utils/directionBadge'

const skills = useSkillsStore()
const directions = useDirectionsStore()
const { confirm } = useConfirm()
const toast = useToast()

onMounted(async () => {
  await Promise.all([skills.fetchAll(), directions.fetchAll()])
})

// Directions -------------------------------------------------------------
const newDirectionName = ref('')
const editingDirectionId = ref<string | null>(null)
const editingDirectionName = ref('')

async function addDirection() {
  const name = newDirectionName.value.trim()
  if (!name) return
  await directions.create(name)
  newDirectionName.value = ''
  toast.success('Направление добавлено')
}

function startEditDirection(id: string, name: string) {
  editingDirectionId.value = id
  editingDirectionName.value = name
}

async function saveDirection() {
  if (!editingDirectionId.value) return
  await directions.rename(editingDirectionId.value, editingDirectionName.value.trim())
  editingDirectionId.value = null
  toast.success('Направление переименовано')
}

async function removeDirection(id: string, name: string) {
  if (skills.items.some((s) => s.directionId === id)) {
    toast.error('Сначала удалите или перенесите навыки этого направления')
    return
  }
  const ok = await confirm(`Удалить направление «${name}»?`, { danger: true, confirmLabel: 'Удалить' })
  if (!ok) return
  await directions.remove(id)
  toast.success('Направление удалено')
}

// Skills -------------------------------------------------------------
const newSkillName = ref<Record<string, string>>({})
const editingSkillId = ref<string | null>(null)
const editingSkillName = ref('')

function skillsFor(directionId: string) {
  return skills.forDirection(directionId)
}

async function addSkill(directionId: string) {
  const name = (newSkillName.value[directionId] ?? '').trim()
  if (!name) return
  await skills.create({ name, directionId })
  newSkillName.value[directionId] = ''
  toast.success('Навык добавлен')
}

function startEditSkill(id: string, name: string) {
  editingSkillId.value = id
  editingSkillName.value = name
}

async function saveSkill() {
  if (!editingSkillId.value) return
  await skills.update(editingSkillId.value, { name: editingSkillName.value.trim() })
  editingSkillId.value = null
  toast.success('Навык переименован')
}

async function removeSkill(id: string, name: string) {
  const ok = await confirm(`Удалить навык «${name}» из справочника? Это не затронет уже сохранённые протоколы встреч.`, {
    danger: true,
    confirmLabel: 'Удалить',
  })
  if (!ok) return
  await skills.remove(id)
  toast.success('Навык удалён')
}

const ready = computed(() => directions.loaded && skills.loaded)
</script>

<template>
  <div class="stack gap-lg">
    <div>
      <h1 class="text-lg">Справочник навыков</h1>
      <p class="text-sm text-muted">Направления и навыки, из которых формируются годовые планы обучения</p>
    </div>

    <BaseCard>
      <p style="font-weight: 700; margin-bottom: 12px">Новое направление</p>
      <div class="row gap-sm">
        <BaseInput v-model="newDirectionName" placeholder="Например, Data Science" @keyup.enter="addDirection" />
        <BaseButton :disabled="!newDirectionName.trim()" @click="addDirection">Добавить</BaseButton>
      </div>
    </BaseCard>

    <div v-if="!ready" class="text-muted">Загрузка…</div>

    <div v-else class="stack gap-md">
      <BaseCard v-for="dir in directions.items" :key="dir.id" :padded="false">
        <div class="dir-header">
          <BaseBadge :variant="directionBadgeVariant(dir.id)">
            <template v-if="editingDirectionId === dir.id">
              <input v-model="editingDirectionName" class="inline-edit" @keyup.enter="saveDirection" />
            </template>
            <template v-else>{{ dir.name }}</template>
          </BaseBadge>
          <span class="text-sm text-faint">{{ skillsFor(dir.id).length }} навыков</span>
          <div class="dir-header__actions">
            <template v-if="editingDirectionId === dir.id">
              <button type="button" class="link-btn" @click="saveDirection">сохранить</button>
              <button type="button" class="link-btn" @click="editingDirectionId = null">отмена</button>
            </template>
            <template v-else>
              <button type="button" class="link-btn" @click="startEditDirection(dir.id, dir.name)">переименовать</button>
              <button type="button" class="link-btn link-btn--danger" @click="removeDirection(dir.id, dir.name)">удалить</button>
            </template>
          </div>
        </div>

        <EmptyState v-if="!skillsFor(dir.id).length" title="Навыков пока нет" />
        <ul v-else class="skill-list">
          <li v-for="s in skillsFor(dir.id)" :key="s.id">
            <template v-if="editingSkillId === s.id">
              <input v-model="editingSkillName" class="inline-edit inline-edit--full" @keyup.enter="saveSkill" />
              <button type="button" class="link-btn" @click="saveSkill">сохранить</button>
              <button type="button" class="link-btn" @click="editingSkillId = null">отмена</button>
            </template>
            <template v-else>
              <span class="skill-list__name">{{ s.name }}</span>
              <button type="button" class="link-btn" @click="startEditSkill(s.id, s.name)">переименовать</button>
              <button type="button" class="link-btn link-btn--danger" @click="removeSkill(s.id, s.name)">удалить</button>
            </template>
          </li>
        </ul>

        <div class="skill-add">
          <BaseInput v-model="newSkillName[dir.id]" placeholder="Новый навык" @keyup.enter="addSkill(dir.id)" />
          <BaseButton size="sm" variant="secondary" @click="addSkill(dir.id)">+ Добавить</BaseButton>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<style scoped>
.dir-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
}

.dir-header__actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.skill-list {
  list-style: none;
  margin: 0;
  padding: 6px 16px;
}

.skill-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
}
.skill-list li:last-child {
  border-bottom: none;
}

.skill-list__name {
  flex: 1;
  font-size: 13.5px;
}

.skill-add {
  display: flex;
  gap: 8px;
  padding: 12px 16px 16px;
}

.link-btn {
  border: none;
  background: none;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 12.5px;
  white-space: nowrap;
}

.link-btn--danger {
  color: var(--color-danger);
}

.inline-edit {
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 12px;
}

.inline-edit--full {
  flex: 1;
  font-size: 13.5px;
  padding: 4px 8px;
}
</style>
