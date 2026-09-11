import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Skill } from '@/types'
import { skillsService } from '@/api/skillsService'

export const useSkillsStore = defineStore('skills', () => {
  const items = ref<Skill[]>([])
  const loaded = ref(false)
  const loading = ref(false)

  const byId = computed(() => new Map(items.value.map((s) => [s.id, s])))

  async function fetchAll(force = false) {
    if (loaded.value && !force) return
    loading.value = true
    try {
      items.value = await skillsService.list()
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  async function create(data: { name: string; directionId: string }) {
    const skill = await skillsService.create(data)
    items.value.push(skill)
    return skill
  }

  async function update(id: string, patch: Partial<Pick<Skill, 'name' | 'directionId'>>) {
    const skill = await skillsService.update(id, patch)
    const idx = items.value.findIndex((s) => s.id === id)
    if (idx !== -1) items.value[idx] = skill
    return skill
  }

  async function remove(id: string) {
    await skillsService.remove(id)
    items.value = items.value.filter((s) => s.id !== id)
  }

  function name(id: string): string {
    return byId.value.get(id)?.name ?? 'Неизвестный навык'
  }

  function forDirection(directionId: string): Skill[] {
    return items.value.filter((s) => s.directionId === directionId)
  }

  return { items, loaded, loading, byId, fetchAll, create, update, remove, name, forDirection }
})
