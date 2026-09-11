import type { PlanItem } from '@/types'
import { http } from './http'

export const plansService = {
  async listAll(): Promise<PlanItem[]> {
    const { data } = await http.get<PlanItem[]>('/plans')
    return data
  },

  async addSkill(data: { userId: string; skillId: string; plannedDate: string }): Promise<PlanItem> {
    const { data: item } = await http.post<PlanItem>('/plans', data)
    return item
  },

  async updatePlannedDate(id: string, plannedDate: string): Promise<PlanItem> {
    const { data } = await http.patch<PlanItem>(`/plans/${id}`, { plannedDate })
    return data
  },

  async remove(id: string): Promise<void> {
    await http.delete(`/plans/${id}`)
  },
}
