import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, permissions, schemas, vk_notify
from ..database import get_db
from ..deps import get_current_user
from ..ids import new_id

router = APIRouter(prefix="/scheduled-meetings", tags=["scheduled-meetings"])
logger = logging.getLogger("scheduled_meetings")


@router.get("", response_model=list[schemas.ScheduledMeetingOut])
async def list_scheduled_meetings(db: AsyncSession = Depends(get_db), _user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.ScheduledMeeting))
    return result.scalars().all()


@router.post("", response_model=schemas.ScheduledMeetingOut, status_code=status.HTTP_201_CREATED)
async def create_scheduled_meeting(
    payload: schemas.ScheduledMeetingCreate,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not await permissions.can_manage(db, user, payload.employee_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Планировать встречу может только руководитель этого сотрудника")

    meeting = models.ScheduledMeeting(
        id=new_id("sched"),
        employee_id=payload.employee_id,
        conducted_by_id=user.id,
        scheduled_date=payload.scheduled_date,
        note=payload.note,
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)

    employee = await db.get(models.User, payload.employee_id)
    if employee and employee.vk_user_id:
        text = f"Запланирована PR-встреча на {payload.scheduled_date.isoformat()}."
        if payload.note:
            text += f"\n{payload.note}"
        try:
            await vk_notify.send_message(employee.vk_user_id, text)
        except Exception:
            logger.exception("Failed to send VK notification for scheduled meeting %s", meeting.id)

    return meeting


@router.delete("/{scheduled_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_scheduled_meeting(
    scheduled_id: str, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)
):
    meeting = await db.get(models.ScheduledMeeting, scheduled_id)
    if not meeting:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Запланированная встреча не найдена")
    if not await permissions.can_manage(db, user, meeting.employee_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")
    await db.delete(meeting)
    await db.commit()
