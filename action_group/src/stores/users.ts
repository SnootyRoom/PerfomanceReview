import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { User } from '@/types'
import { usersService, type CreateUserInput } from '@/api/usersService'
import { useAuthStore } from './auth'

export const useUsersStore = defineStore('users', () => {
  const items = ref<User[]>([])
  const loaded = ref(false)
  const loading = ref(false)

  const byId = computed(() => new Map(items.value.map((u) => [u.id, u])))

  async function fetchAll(force = false) {
    if (loaded.value && !force) return
    loading.value = true
    try {
      items.value = await usersService.list()
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  async function create(data: CreateUserInput) {
    const user = await usersService.create(data)
    items.value.push(user)
    return user
  }

  async function update(
    id: string,
    patch: Partial<Pick<User, 'fullName' | 'login' | 'directionId' | 'departmentId' | 'isAdmin'>> & {
      password?: string
    },
  ) {
    const user = await usersService.update(id, patch)
    const idx = items.value.findIndex((u) => u.id === id)
    if (idx !== -1) items.value[idx] = user
    useAuthStore().refreshUser(user)
    return user
  }

  async function remove(id: string) {
    await usersService.remove(id)
    items.value = items.value.filter((u) => u.id !== id)
  }

  function fullName(id: string | null): string {
    if (!id) return '—'
    return byId.value.get(id)?.fullName ?? 'Неизвестный пользователь'
  }

  return { items, loaded, loading, byId, fetchAll, create, update, remove, fullName }
})
