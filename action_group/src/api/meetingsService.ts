import type { Attachment, Meeting, ProblemFlag, SkillMark } from '@/types'
import { http } from './http'

export interface MeetingInput {
  employeeId: string
  date: string
  summaryMarkdown: string
  attachments: Omit<Attachment, 'id'>[]
  skillMarks: SkillMark[]
  problems: Omit<ProblemFlag, 'id' | 'resolvedAt'>[]
}

export const meetingsService = {
  async list(): Promise<Meeting[]> {
    const { data } = await http.get<Meeting[]>('/meetings')
    return data
  },

  async create(data: MeetingInput): Promise<Meeting> {
    const { data: meeting } = await http.post<Meeting>('/meetings', data)
    return meeting
  },

  async setProblemResolved(meetingId: string, problemId: string, resolved: boolean): Promise<void> {
    await http.patch(`/meetings/${meetingId}/problems/${problemId}`, { resolved })
  },
}
