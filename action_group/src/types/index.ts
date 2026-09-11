// Field-for-field mirror of the FastAPI backend's Pydantic response schemas
// (see backend/app/schemas.py, which camelCase-aliases everything to match).

// Data, not a hardcoded enum: directions must be admin-editable.
export interface SkillDirection {
  id: string
  name: string
}

export interface Department {
  id: string
  name: string
  parentId: string | null
  managerId: string | null
}

export interface User {
  id: string
  fullName: string
  login: string
  directionId: string
  departmentId: string | null
  isAdmin: boolean
  avatarColor: string
  vkUserId: string | null
  createdAt: string
}

export interface Skill {
  id: string
  name: string
  directionId: string
}

export type PlanItemStatus = 'planned' | 'confirmed' | 'problem'

export interface PlanItem {
  id: string
  userId: string
  skillId: string
  plannedDate: string // ISO date
  status: PlanItemStatus
  confirmedDate: string | null
  confirmedInMeetingId: string | null
}

export type AttachmentType = 'file' | 'link'

export interface Attachment {
  id: string
  type: AttachmentType
  name: string
  url: string
}

export interface SkillMark {
  skillId: string
  /** true = skill confirmed during this meeting, false = discussed only */
  confirmed: boolean
  comment: string
}

export interface ProblemFlag {
  id: string
  /** scope 'skill' targets a specific skill, 'employee' is a general concern */
  scope: 'skill' | 'employee'
  skillId: string | null
  comment: string
  resolved: boolean
  resolvedAt: string | null // ISO date, set when resolved toggles true
}

export interface Meeting {
  id: string
  employeeId: string
  conductedById: string
  date: string // ISO date
  summaryMarkdown: string
  attachments: Attachment[]
  skillMarks: SkillMark[]
  problems: ProblemFlag[]
  createdAt: string
}

export interface ScheduledMeeting {
  id: string
  employeeId: string
  conductedById: string
  scheduledDate: string // ISO date
  note: string
  createdAt: string
}

export interface AuthSession {
  userId: string
  token: string
}
