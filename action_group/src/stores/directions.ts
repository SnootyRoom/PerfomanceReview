import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { SkillDirection } from '@/types'
import { directionsService } from '@/api/directionsService'

export const useDirectionsStore = defineStore('directions', () => {
  const items = ref<SkillDirection[]>([])
  const loaded = ref(false)
  const loading = ref(false)

  const byId = computed(() => new Map(items.value.map((d) => [d.id, d])))

  async function fetchAll(force = false) {
    if (loaded.value && !force) return
    loading.value = true
    try {
      items.value = await directionsService.list()
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  async function create(name: string) {
    const direction = await directionsService.create(name)
    items.value.push(direction)
    return direction
  }

  async function rename(id: string, name: string) {
    const direction = await directionsService.rename(id, name)
    const idx = items.value.findIndex((d) => d.id === id)
    if (idx !== -1) items.value[idx] = direction
    return direction
  }

  async function remove(id: string) {
    await directionsService.remove(id)
    items.value = items.value.filter((d) => d.id !== id)
  }

  function name(id: string): string {
    return byId.value.get(id)?.name ?? 'Без направления'
  }

  return { items, loaded, loading, byId, fetchAll, create, rename, remove, name }
})
