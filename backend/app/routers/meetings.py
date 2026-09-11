import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import models, permissions, schemas, vk_notify
from ..database import get_db
from ..deps import get_current_user
from ..ids import new_id

router = APIRouter(prefix="/meetings", tags=["meetings"])
logger = logging.getLogger("meetings")


def _with_relations():
    return (
        selectinload(models.Meeting.attachments),
        selectinload(models.Meeting.skill_marks),
        selectinload(models.Meeting.problems),
    )


@router.get("", response_model=list[schemas.MeetingOut])
async def list_meetings(db: AsyncSession = Depends(get_db), _user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Meeting).options(*_with_relations()))
    return result.scalars().unique().all()


@router.get("/{meeting_id}", response_model=schemas.MeetingOut)
async def get_meeting(
    meeting_id: str, db: AsyncSession = Depends(get_db), _user: models.User = Depends(get_current_user)
):
    result = await db.execute(select(models.Meeting).options(*_with_relations()).where(models.Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Встреча не найдена")
    return meeting


@router.post("", response_model=schemas.MeetingOut, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    payload: schemas.MeetingCreate,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not await permissions.can_manage(db, user, payload.employee_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Проводить встречу может только руководитель этого сотрудника")

    meeting = models.Meeting(
        id=new_id("meeting"),
        employee_id=payload.employee_id,
        conducted_by_id=user.id,
        date=payload.date,
        summary_markdown=payload.summary_markdown,
    )
    db.add(meeting)
    for a in payload.attachments:
        db.add(models.Attachment(id=new_id("att"), meeting_id=meeting.id, type=a.type, name=a.name, url=a.url))
    for m in payload.skill_marks:
        db.add(
            models.SkillMark(
                id=new_id("mark"), meeting_id=meeting.id, skill_id=m.skill_id, confirmed=m.confirmed, comment=m.comment
            )
        )
    for p in payload.problems:
        db.add(
            models.ProblemFlag(
                id=new_id("problem"),
                meeting_id=meeting.id,
                scope=p.scope,
                skill_id=p.skill_id,
                comment=p.comment,
                resolved=p.resolved,
            )
        )

    # A failed re-check reverts an already-confirmed plan entry instead of
    # being ignored, so a past pass doesn't linger forever after a regression.
    for m in payload.skill_marks:
        existing = await db.execute(
            select(models.PlanItem).where(
                models.PlanItem.user_id == payload.employee_id, models.PlanItem.skill_id == m.skill_id
            )
        )
        item = existing.scalar_one_or_none()
        if m.confirmed:
            if item:
                item.confirmed = True
                item.confirmed_date = payload.date
                item.confirmed_in_meeting_id = meeting.id
            else:
                db.add(
                    models.PlanItem(
                        id=new_id("plan"),
                        user_id=payload.employee_id,
                        skill_id=m.skill_id,
                        planned_date=payload.date,
                        confirmed=True,
                        confirmed_date=payload.date,
                        confirmed_in_meeting_id=meeting.id,
                    )
                )
        elif item and item.confirmed:
            item.confirmed = False
            item.confirmed_date = None
            item.confirmed_in_meeting_id = None

    # A protocol now covers this date, so any scheduled meeting due by then is stale.
    stale = await db.execute(
        select(models.ScheduledMeeting).where(
            models.ScheduledMeeting.employee_id == payload.employee_id,
            models.ScheduledMeeting.scheduled_date <= payload.date,
        )
    )
    for s in stale.scalars().all():
        await db.delete(s)

    await db.commit()
    result = await db.execute(select(models.Meeting).options(*_with_relations()).where(models.Meeting.id == meeting.id))
    saved = result.scalar_one()

    employee = await db.get(models.User, payload.employee_id)
    if employee and employee.vk_user_id:
        confirmed_count = sum(1 for m in payload.skill_marks if m.confirmed)
        problems_count = len(payload.problems)
        text = (
            f"Зафиксирован протокол встречи от {payload.date.isoformat()}.\n"
            f"Подтверждено навыков: {confirmed_count}."
            + (f" Отмечено проблем: {problems_count}." if problems_count else "")
        )
        try:
            await vk_notify.send_message(employee.vk_user_id, text)
        except Exception:  # best-effort notification must never break the request
            logger.exception("Failed to send VK notification for meeting %s", meeting.id)

    return saved


@router.patch("/{meeting_id}/problems/{problem_id}", response_model=schemas.ProblemFlagOut)
async def set_problem_resolved(
    meeting_id: str,
    problem_id: str,
    payload: schemas.ProblemResolveUpdate,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    meeting = await db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Встреча не найдена")
    if not await permissions.can_manage(db, user, meeting.employee_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")
    problem = await db.get(models.ProblemFlag, problem_id)
    if not problem or problem.meeting_id != meeting_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Проблема не найдена")
    problem.resolved = payload.resolved
    problem.resolved_at = datetime.date.today() if payload.resolved else None
    await db.commit()
    await db.refresh(problem)
    return problem


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: str, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)
):
    meeting = await db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Встреча не найдена")
    if not await permissions.can_manage(db, user, meeting.employee_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")
    await db.delete(meeting)
    await db.commit()
