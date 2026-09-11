import datetime

from sqlalchemy import Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Direction(Base):
    __tablename__ = "directions"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))
    manager_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", use_alter=True, name="fk_department_manager", ondelete="SET NULL")
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    full_name: Mapped[str]
    login: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    direction_id: Mapped[str] = mapped_column(ForeignKey("directions.id"))
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar_color: Mapped[str]
    vk_user_id: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime.date] = mapped_column(Date)


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    direction_id: Mapped[str] = mapped_column(ForeignKey("directions.id"))


class PlanItem(Base):
    __tablename__ = "plan_items"

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"))
    planned_date: Mapped[datetime.date] = mapped_column(Date)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed_date: Mapped[datetime.date | None] = mapped_column(Date, default=None)
    confirmed_in_meeting_id: Mapped[str | None] = mapped_column(
        ForeignKey("meetings.id", ondelete="SET NULL"), default=None
    )
    reminder_sent_at: Mapped[datetime.date | None] = mapped_column(Date, default=None)


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[str] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    conducted_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    date: Mapped[datetime.date] = mapped_column(Date)
    summary_markdown: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)

    attachments: Mapped[list["Attachment"]] = relationship(cascade="all, delete-orphan")
    skill_marks: Mapped[list["SkillMark"]] = relationship(cascade="all, delete-orphan")
    problems: Mapped[list["ProblemFlag"]] = relationship(cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(primary_key=True)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    type: Mapped[str]  # "file" | "link"
    name: Mapped[str]
    url: Mapped[str] = mapped_column(Text)


class SkillMark(Base):
    __tablename__ = "skill_marks"

    id: Mapped[str] = mapped_column(primary_key=True)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"))
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    comment: Mapped[str] = mapped_column(Text, default="")


class ScheduledMeeting(Base):
    """A future PR-meeting a manager plans for a subordinate — distinct from
    Meeting, which is the protocol written up after the meeting happened."""

    __tablename__ = "scheduled_meetings"

    id: Mapped[str] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    conducted_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    scheduled_date: Mapped[datetime.date] = mapped_column(Date)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)


class ProblemFlag(Base):
    __tablename__ = "problem_flags"

    id: Mapped[str] = mapped_column(primary_key=True)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    scope: Mapped[str]  # "skill" | "employee"
    skill_id: Mapped[str | None] = mapped_column(ForeignKey("skills.id", ondelete="SET NULL"), default=None)
    comment: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime.date | None] = mapped_column(Date, default=None)
