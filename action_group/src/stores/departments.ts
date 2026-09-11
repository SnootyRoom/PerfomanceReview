import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Department } from '@/types'
import { departmentsService, buildTree, getAncestorIds, getDescendantIds } from '@/api/departmentsService'

export const useDepartmentsStore = defineStore('departments', () => {
  const items = ref<Department[]>([])
  const loaded = ref(false)
  const loading = ref(false)

  const byId = computed(() => new Map(items.value.map((d) => [d.id, d])))
  const tree = computed(() => buildTree(items.value))

  async function fetchAll(force = false) {
    if (loaded.value && !force) return
    loading.value = true
    try {
      items.value = await departmentsService.list()
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  async function create(data: { name: string; parentId: string | null; managerId: string | null }) {
    const dept = await departmentsService.create(data)
    items.value.push(dept)
    return dept
  }

  async function update(id: string, patch: Partial<Pick<Department, 'name' | 'parentId' | 'managerId'>>) {
    const dept = await departmentsService.update(id, patch)
    const idx = items.value.findIndex((d) => d.id === id)
    if (idx !== -1) items.value[idx] = dept
    return dept
  }

  async function remove(id: string) {
    await departmentsService.remove(id)
    items.value = items.value.filter((d) => d.id !== id)
  }

  function ancestorsOf(deptId: string): string[] {
    return getAncestorIds(deptId, items.value)
  }

  function descendantsOf(deptId: string): string[] {
    return getDescendantIds(deptId, items.value)
  }

  function pathLabel(deptId: string | null): string {
    if (!deptId) return '—'
    const chain = [deptId, ...ancestorsOf(deptId)].reverse()
    return chain.map((id) => byId.value.get(id)?.name ?? '?').join(' / ')
  }

  return {
    items,
    loaded,
    loading,
    byId,
    tree,
    fetchAll,
    create,
    update,
    remove,
    ancestorsOf,
    descendantsOf,
    pathLabel,
  }
})
