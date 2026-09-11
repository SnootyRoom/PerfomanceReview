import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'
import { useDepartmentsStore } from '@/stores/departments'

// Access is not a fixed role — it's derived from the viewer's position in
// the department tree relative to the profile being viewed, so every check
// below is a function of (viewerId, targetId), never a static role flag.
export function usePermissions() {
  const auth = useAuthStore()
  const users = useUsersStore()
  const departments = useDepartmentsStore()

  const viewerId = computed(() => auth.currentUser?.id ?? null)
  const isAdmin = computed(() => auth.currentUser?.isAdmin === true)

  /** True if `managerId` manages the department chain that `targetId` belongs to. */
  function managesEmployee(managerId: string, targetId: string): boolean {
    const target = users.byId.get(targetId)
    if (!target || !target.departmentId) return false
    const chain = [target.departmentId, ...departments.ancestorsOf(target.departmentId)]
    return chain.some((deptId) => departments.byId.get(deptId)?.managerId === managerId)
  }

  function canView(targetId: string): boolean {
    if (isAdmin.value) return true
    if (!viewerId.value) return false
    if (viewerId.value === targetId) return true
    return managesEmployee(viewerId.value, targetId)
  }

  /** Running PR meetings, editing the plan, handling problems for this employee. */
  function canManage(targetId: string): boolean {
    if (isAdmin.value) return true
    if (!viewerId.value) return false
    return managesEmployee(viewerId.value, targetId)
  }

  const managedEmployeeIds = computed<Set<string>>(() => {
    if (!viewerId.value) return new Set()
    const ids = users.items.filter((u) => u.id !== viewerId.value && managesEmployee(viewerId.value!, u.id)).map((u) => u.id)
    return new Set(ids)
  })

  const visibleEmployeeIds = computed<Set<string>>(() => {
    if (isAdmin.value) return new Set(users.items.map((u) => u.id))
    if (!viewerId.value) return new Set()
    return new Set([viewerId.value, ...managedEmployeeIds.value])
  })

  const hasSubordinates = computed(() => managedEmployeeIds.value.size > 0)

  /** Departments directly or transitively managed by the viewer (for scoping the org tree / filters). */
  const managedDepartmentIds = computed<Set<string>>(() => {
    if (!viewerId.value) return new Set()
    const owned = departments.items.filter((d) => d.managerId === viewerId.value).map((d) => d.id)
    const all = new Set(owned)
    for (const id of owned) departments.descendantsOf(id).forEach((d) => all.add(d))
    return all
  })

  return {
    isAdmin,
    canView,
    canManage,
    managesEmployee,
    managedEmployeeIds,
    visibleEmployeeIds,
    hasSubordinates,
    managedDepartmentIds,
  }
}
