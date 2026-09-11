import type { ScheduledMeeting } from '@/types'
import { http } from './http'

export const scheduledMeetingsService = {
  async list(): Promise<ScheduledMeeting[]> {
    const { data } = await http.get<ScheduledMeeting[]>('/scheduled-meetings')
    return data
  },

  async create(data: { employeeId: string; scheduledDate: string; note: string }): Promise<ScheduledMeeting> {
    const { data: meeting } = await http.post<ScheduledMeeting>('/scheduled-meetings', data)
    return meeting
  },

  async remove(id: string): Promise<void> {
    await http.delete(`/scheduled-meetings/${id}`)
  },
}
