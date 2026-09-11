<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useUsersStore } from '@/stores/users'
import { useDepartmentsStore } from '@/stores/departments'
import { useDirectionsStore } from '@/stores/directions'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'
import type { User } from '@/types'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import UserAvatar from '@/components/ui/UserAvatar.vue'
import { directionBadgeVariant } from '@/utils/directionBadge'
import { Pencil, Trash2 } from '@lucide/vue'

const users = useUsersStore()
const departments = useDepartmentsStore()
const directions = useDirectionsStore()
const auth = useAuthStore()
const { confirm } = useConfirm()
const toast = useToast()

onMounted(async () => {
  await Promise.all([users.fetchAll(), departments.fetchAll(), directions.fetchAll()])
})

const search = ref('')
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return users.items
  return users.items.filter((u) => u.fullName.toLowerCase().includes(q) || u.login.toLowerCase().includes(q))
})

const showModal = ref(false)
const editingId = ref<string | null>(null)
const saving = ref(false)
const formError = ref('')
const form = ref({
  fullName: '',
  login: '',
  password: '',
  directionId: '',
  departmentId: '',
  isAdmin: false,
})

function openCreate() {
  editingId.value = null
  form.value = {
    fullName: '',
    login: '',
    password: '',
    directionId: directions.items[0]?.id ?? '',
    departmentId: '',
    isAdmin: false,
  }
  formError.value = ''
  showModal.value = true
}

function openEdit(u: User) {
  editingId.value = u.id
  form.value = {
    fullName: u.fullName,
    login: u.login,
    password: '',
    directionId: u.directionId,
    departmentId: u.departmentId ?? '',
    isAdmin: u.isAdmin,
  }
  formError.value = ''
  showModal.value = true
}

async function submit() {
  if (!form.value.fullName.trim() || !form.value.login.trim()) {
    formError.value = 'Заполните ФИО и логин'
    return
  }
  if (!editingId.value && !form.value.password.trim()) {
    formError.value = 'Укажите пароль для нового пользователя'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    if (editingId.value) {
      const patch: Record<string, unknown> = {
        fullName: form.value.fullName.trim(),
        login: form.value.login.trim(),
        directionId: form.value.directionId,
        departmentId: form.value.departmentId || null,
        isAdmin: form.value.isAdmin,
      }
      if (form.value.password.trim()) patch.password = form.value.password.trim()
      await users.update(editingId.value, patch)
      toast.success('Пользователь обновлён')
    } else {
      await users.create({
        fullName: form.value.fullName.trim(),
        login: form.value.login.trim(),
        password: form.value.password.trim(),
        directionId: form.value.directionId,
        departmentId: form.value.departmentId || null,
        isAdmin: form.value.isAdmin,
      })
      toast.success('Пользователь создан')
    }
    showModal.value = false
  } catch (e) {
    formError.value = e instanceof Error ? e.message : 'Не удалось сохранить'
  } finally {
    saving.value = false
  }
}

async function removeUser(u: User) {
  if (u.id === auth.currentUser?.id) {
    toast.error('Нельзя удалить собственную учётную запись')
    return
  }
  if (departments.items.some((d) => d.managerId === u.id)) {
    toast.error('Сначала назначьте другого руководителя в подразделениях этого пользователя')
    return
  }
  const ok = await confirm(`Удалить пользователя «${u.fullName}»?`, { danger: true, confirmLabel: 'Удалить' })
  if (!ok) return
  await users.remove(u.id)
  toast.success('Пользователь удалён')
}

const departmentOptions = computed(() => [
  { value: '', label: '— без подразделения —' },
  ...departments.items.map((d) => ({ value: d.id, label: departments.pathLabel(d.id) })),
])
const directionOptions = computed(() => directions.items.map((d) => ({ value: d.id, label: d.name })))
</script>

<template>
  <div class="stack gap-lg">
    <div class="row gap-md" style="justify-content: space-between; flex-wrap: wrap">
      <div>
        <h1 class="text-lg">Пользователи</h1>
        <p class="text-sm text-muted">Учётные записи, направления и привязка к подразделениям</p>
      </div>
      <BaseButton size="sm" @click="openCreate">+ Новый пользователь</BaseButton>
    </div>

    <BaseCard>
      <BaseInput v-model="search" placeholder="Поиск по имени или логину" />
    </BaseCard>

    <BaseCard :padded="false">
      <ul class="user-list">
        <li v-for="u in filtered" :key="u.id">
          <UserAvatar :name="u.fullName" :color="u.avatarColor" :size="36" />
          <div class="user-list__body">
            <p class="user-list__name">{{ u.fullName }} <span class="text-sm text-faint">@{{ u.login }}</span></p>
            <p class="text-sm text-muted">{{ departments.pathLabel(u.departmentId) }}</p>
          </div>
          <BaseBadge :variant="directionBadgeVariant(u.directionId)">{{ directions.name(u.directionId) }}</BaseBadge>
          <BaseBadge v-if="u.isAdmin" variant="info">Админ</BaseBadge>
          <div class="row gap-xs">
            <button type="button" class="icon-btn" title="Редактировать" @click="openEdit(u)"><Pencil :size="14" /></button>
            <button type="button" class="icon-btn" title="Удалить" @click="removeUser(u)"><Trash2 :size="14" /></button>
          </div>
        </li>
      </ul>
    </BaseCard>

    <BaseModal v-if="showModal" :title="editingId ? 'Редактировать пользователя' : 'Новый пользователь'" @close="showModal = false">
      <div class="stack gap-md">
        <BaseInput v-model="form.fullName" label="ФИО" required />
        <BaseInput v-model="form.login" label="Логин" required />
        <BaseInput v-model="form.password" type="password" :label="editingId ? 'Новый пароль (необязательно)' : 'Пароль'" :required="!editingId" />
        <BaseSelect v-model="form.directionId" label="Направление" :options="directionOptions" />
        <BaseSelect v-model="form.departmentId" label="Подразделение" :options="departmentOptions" />
        <label class="checkbox-field">
          <input v-model="form.isAdmin" type="checkbox" />
          Администратор системы
        </label>
        <p v-if="formError" class="text-sm" style="color: var(--color-danger)">{{ formError }}</p>
      </div>
      <template #footer>
        <BaseButton variant="secondary" @click="showModal = false">Отмена</BaseButton>
        <BaseButton :loading="saving" @click="submit">Сохранить</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.user-list {
  list-style: none;
  margin: 0;
  padding: 6px;
}

.user-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-bottom: 1px solid var(--color-border);
}
.user-list li:last-child {
  border-bottom: none;
}

.user-list__body {
  flex: 1;
  min-width: 0;
}

.user-list__name {
  font-weight: 600;
  font-size: 14px;
}

.icon-btn {
  border: none;
  background: var(--color-surface-alt);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
}
.icon-btn:hover {
  background: var(--color-border);
}

.checkbox-field {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
}

@media (max-width: 640px) {
  .user-list__name span {
    display: block;
  }
}
</style>
