<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDepartmentsStore } from '@/stores/departments'
import { useUsersStore } from '@/stores/users'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import DepartmentNode from '@/components/departments/DepartmentNode.vue'

const departments = useDepartmentsStore()
const users = useUsersStore()
const { confirm } = useConfirm()
const toast = useToast()

onMounted(async () => {
  await Promise.all([departments.fetchAll(), users.fetchAll()])
})

function employeeCount(deptId: string): number {
  return users.items.filter((u) => u.departmentId === deptId).length
}

const showModal = ref(false)
const editingId = ref<string | null>(null)
const form = ref({ name: '', parentId: '', managerId: '' })
const saving = ref(false)
const formError = ref('')

const parentOptions = computed(() => {
  const excluded = new Set<string>()
  if (editingId.value) {
    excluded.add(editingId.value)
    departments.descendantsOf(editingId.value).forEach((id) => excluded.add(id))
  }
  return [
    { value: '', label: '— корень (без родителя) —' },
    ...departments.items
      .filter((d) => !excluded.has(d.id))
      .map((d) => ({ value: d.id, label: departments.pathLabel(d.id) })),
  ]
})

const managerOptions = computed(() => [
  { value: '', label: '— не назначен —' },
  ...users.items.map((u) => ({ value: u.id, label: `${u.fullName} (${u.login})` })),
])

function openCreate(parentId: string | null) {
  editingId.value = null
  form.value = { name: '', parentId: parentId ?? '', managerId: '' }
  formError.value = ''
  showModal.value = true
}

function openEdit(id: string) {
  const dept = departments.byId.get(id)
  if (!dept) return
  editingId.value = id
  form.value = { name: dept.name, parentId: dept.parentId ?? '', managerId: dept.managerId ?? '' }
  formError.value = ''
  showModal.value = true
}

async function submit() {
  if (!form.value.name.trim()) {
    formError.value = 'Укажите название подразделения'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    const payload = {
      name: form.value.name.trim(),
      parentId: form.value.parentId || null,
      managerId: form.value.managerId || null,
    }
    if (editingId.value) {
      await departments.update(editingId.value, payload)
      toast.success('Подразделение обновлено')
    } else {
      await departments.create(payload)
      toast.success('Подразделение создано')
    }
    showModal.value = false
  } catch (e) {
    formError.value = e instanceof Error ? e.message : 'Не удалось сохранить'
  } finally {
    saving.value = false
  }
}

async function removeDept(id: string) {
  const hasChildren = departments.items.some((d) => d.parentId === id)
  const hasEmployees = employeeCount(id) > 0
  if (hasChildren || hasEmployees) {
    toast.error('Сначала перенесите дочерние подразделения и сотрудников в другой узел')
    return
  }
  const dept = departments.byId.get(id)
  const ok = await confirm(`Удалить подразделение «${dept?.name}»?`, { danger: true, confirmLabel: 'Удалить' })
  if (!ok) return
  await departments.remove(id)
  toast.success('Подразделение удалено')
}
</script>

<template>
  <div class="stack gap-lg">
    <div class="row gap-md" style="justify-content: space-between; flex-wrap: wrap">
      <div>
        <h1 class="text-lg">Структура подразделений</h1>
        <p class="text-sm text-muted">Дерево произвольной вложенности, у каждого узла — свой руководитель</p>
      </div>
      <BaseButton size="sm" @click="openCreate(null)">+ Новое подразделение</BaseButton>
    </div>

    <EmptyState v-if="!departments.tree.length" title="Подразделений пока нет">
      <template #action>
        <BaseButton @click="openCreate(null)">Создать первое подразделение</BaseButton>
      </template>
    </EmptyState>

    <BaseCard v-else :padded="false">
      <DepartmentNode
        v-for="root in departments.tree"
        :key="root.id"
        :node="root"
        :depth="0"
        :employee-count="employeeCount"
        @add-child="openCreate"
        @edit="openEdit"
        @remove="removeDept"
      />
    </BaseCard>

    <BaseModal v-if="showModal" :title="editingId ? 'Редактировать подразделение' : 'Новое подразделение'" @close="showModal = false">
      <div class="stack gap-md">
        <BaseInput v-model="form.name" label="Название" required />
        <BaseSelect v-model="form.parentId" label="Родительское подразделение" :options="parentOptions" />
        <BaseSelect v-model="form.managerId" label="Руководитель" :options="managerOptions" />
        <p v-if="formError" class="text-sm" style="color: var(--color-danger)">{{ formError }}</p>
      </div>
      <template #footer>
        <BaseButton variant="secondary" @click="showModal = false">Отмена</BaseButton>
        <BaseButton :loading="saving" @click="submit">Сохранить</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>
