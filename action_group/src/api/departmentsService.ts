import type { Department } from '@/types'
import { http } from './http'

/** All ancestor ids from the department up to (and excluding) the root, nearest first. */
export function getAncestorIds(deptId: string, all: Department[]): string[] {
  const byId = new Map(all.map((d) => [d.id, d]))
  const result: string[] = []
  let current = byId.get(deptId)?.parentId ?? null
  while (current) {
    result.push(current)
    current = byId.get(current)?.parentId ?? null
  }
  return result
}

/** All descendant department ids (not including the department itself). */
export function getDescendantIds(deptId: string, all: Department[]): string[] {
  const children = all.filter((d) => d.parentId === deptId)
  const result: string[] = []
  for (const child of children) {
    result.push(child.id, ...getDescendantIds(child.id, all))
  }
  return result
}

export interface DepartmentNode extends Department {
  children: DepartmentNode[]
}

export function buildTree(all: Department[]): DepartmentNode[] {
  const nodes = new Map<string, DepartmentNode>(all.map((d) => [d.id, { ...d, children: [] }]))
  const roots: DepartmentNode[] = []
  for (const node of nodes.values()) {
    if (node.parentId && nodes.has(node.parentId)) {
      nodes.get(node.parentId)!.children.push(node)
    } else {
      roots.push(node)
    }
  }
  return roots
}

export const departmentsService = {
  async list(): Promise<Department[]> {
    const { data } = await http.get<Department[]>('/departments')
    return data
  },

  async create(data: { name: string; parentId: string | null; managerId: string | null }): Promise<Department> {
    const { data: dept } = await http.post<Department>('/departments', data)
    return dept
  },

  async update(id: string, patch: Partial<Pick<Department, 'name' | 'parentId' | 'managerId'>>): Promise<Department> {
    const { data } = await http.patch<Department>(`/departments/${id}`, patch)
    return data
  },

  async remove(id: string): Promise<void> {
    await http.delete(`/departments/${id}`)
  },
}
