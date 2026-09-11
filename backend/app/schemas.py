import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

# Every schema below mirrors src/types/index.ts field-for-field via camelCase
# aliasing, so the frontend needed zero type changes when it switched from
# the localStorage mock to this API.


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


# --- Directions -----------------------------------------------------------


class DirectionOut(CamelModel):
    id: str
    name: str


class DirectionCreate(BaseModel):
    name: str


class DirectionUpdate(BaseModel):
    name: str


# --- Departments ------------------------------------------------------------


class DepartmentOut(CamelModel):
    id: str
    name: str
    parent_id: str | None
    manager_id: str | None


class DepartmentCreate(CamelModel):
    name: str
    parent_id: str | None = None
    manager_id: str | None = None


class DepartmentUpdate(CamelModel):
    name: str | None = None
    parent_id: str | None = None
    manager_id: str | None = None


# --- Users ------------------------------------------------------------------


class UserOut(CamelModel):
    id: str
    full_name: str
    login: str
    direction_id: str
    department_id: str | None
    is_admin: bool
    avatar_color: str
    vk_user_id: str | None
    created_at: datetime.date


class UserCreate(CamelModel):
    full_name: str
    login: str
    password: str
    direction_id: str
    department_id: str | None = None
    is_admin: bool = False


class UserUpdate(CamelModel):
    full_name: str | None = None
    login: str | None = None
    password: str | None = None
    direction_id: str | None = None
    department_id: str | None = None
    is_admin: bool | None = None


class NotificationSettingsUpdate(CamelModel):
    vk_user_id: str | None = None


# --- Skills -------------------------------------------------------------------


class SkillOut(CamelModel):
    id: str
    name: str
    direction_id: str


class SkillCreate(CamelModel):
    name: str
    direction_id: str


class SkillUpdate(CamelModel):
    name: str | None = None
    direction_id: str | None = None


# --- Plan items ---------------------------------------------------------------

PlanItemStatus = Literal["planned", "confirmed", "problem"]


class PlanItemOut(CamelModel):
    id: str
    user_id: str
    skill_id: str
    planned_date: datetime.date
    status: PlanItemStatus
    confirmed_date: datetime.date | None
    confirmed_in_meeting_id: str | None

    @staticmethod
    def from_orm_item(item) -> "PlanItemOut":
        if item.confirmed:
            status: PlanItemStatus = "confirmed"
        elif item.planned_date < datetime.date.today():
            status = "problem"
        else:
            status = "planned"
        return PlanItemOut(
            id=item.id,
            user_id=item.user_id,
            skill_id=item.skill_id,
            planned_date=item.planned_date,
            status=status,
            confirmed_date=item.confirmed_date,
            confirmed_in_meeting_id=item.confirmed_in_meeting_id,
        )


class PlanItemCreate(CamelModel):
    user_id: str
    skill_id: str
    planned_date: datetime.date


class PlanItemUpdate(CamelModel):
    planned_date: datetime.date


# --- Meetings -------------------------------------------------------------------


class AttachmentIn(BaseModel):
    type: Literal["file", "link"]
    name: str
    url: str


class AttachmentOut(CamelModel):
    id: str
    type: Literal["file", "link"]
    name: str
    url: str


class SkillMarkIn(CamelModel):
    skill_id: str
    confirmed: bool
    comment: str = ""


class SkillMarkOut(CamelModel):
    skill_id: str
    confirmed: bool
    comment: str


class ProblemFlagIn(CamelModel):
    scope: Literal["skill", "employee"]
    skill_id: str | None = None
    comment: str
    resolved: bool = False


class ProblemFlagOut(CamelModel):
    id: str
    scope: Literal["skill", "employee"]
    skill_id: str | None
    comment: str
    resolved: bool
    resolved_at: datetime.date | None


class MeetingCreate(CamelModel):
    employee_id: str
    date: datetime.date
    summary_markdown: str
    attachments: list[AttachmentIn] = []
    skill_marks: list[SkillMarkIn] = []
    problems: list[ProblemFlagIn] = []


class MeetingOut(CamelModel):
    id: str
    employee_id: str
    conducted_by_id: str
    date: datetime.date
    summary_markdown: str
    attachments: list[AttachmentOut]
    skill_marks: list[SkillMarkOut]
    problems: list[ProblemFlagOut]
    created_at: datetime.date


class ProblemResolveUpdate(CamelModel):
    resolved: bool


# --- Scheduled meetings (timeline / planning bonus feature) -------------------


class ScheduledMeetingOut(CamelModel):
    id: str
    employee_id: str
    conducted_by_id: str
    scheduled_date: datetime.date
    note: str
    created_at: datetime.date


class ScheduledMeetingCreate(CamelModel):
    employee_id: str
    scheduled_date: datetime.date
    note: str = ""


# --- AI analysis (GigaChat) ----------------------------------------------------


class AiAnalysisOut(BaseModel):
    text: str


# --- Auth -----------------------------------------------------------------------


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(CamelModel):
    token: str
    user: UserOut


class VkTestNotification(BaseModel):
    message: str = "Тестовое уведомление из Performance Review"
