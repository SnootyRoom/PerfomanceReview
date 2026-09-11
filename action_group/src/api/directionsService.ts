import type { SkillDirection } from '@/types'
import { http } from './http'

export const directionsService = {
  async list(): Promise<SkillDirection[]> {
    const { data } = await http.get<SkillDirection[]>('/directions')
    return data
  },

  async create(name: string): Promise<SkillDirection> {
    const { data } = await http.post<SkillDirection>('/directions', { name })
    return data
  },

  async rename(id: string, name: string): Promise<SkillDirection> {
    const { data } = await http.patch<SkillDirection>(`/directions/${id}`, { name })
    return data
  },

  async remove(id: string): Promise<void> {
    await http.delete(`/directions/${id}`)
  },
}
