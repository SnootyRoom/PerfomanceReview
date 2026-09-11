import datetime
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from . import models, vk_notify
from .config import settings
from .database import SessionLocal

logger = logging.getLogger("scheduler")


async def check_upcoming_plan_dates() -> None:
    """Reminds employees in VK about training-plan skills whose planned
    confirmation date is coming up soon, once per item (reminder_sent_at
    guards against re-notifying every run)."""
    if not vk_notify.is_configured():
        return

    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=settings.vk_reminder_days_ahead)

    async with SessionLocal() as db:
        result = await db.execute(
            select(models.PlanItem).where(
                models.PlanItem.confirmed.is_(False),
                models.PlanItem.planned_date >= today,
                models.PlanItem.planned_date <= horizon,
                models.PlanItem.reminder_sent_at.is_(None),
            )
        )
        items = result.scalars().all()
        if not items:
            return

        skill_ids = {i.skill_id for i in items}
        user_ids = {i.user_id for i in items}
        skills = {
            s.id: s for s in (await db.execute(select(models.Skill).where(models.Skill.id.in_(skill_ids)))).scalars()
        }
        users = {
            u.id: u for u in (await db.execute(select(models.User).where(models.User.id.in_(user_ids)))).scalars()
        }

        for item in items:
            user = users.get(item.user_id)
            skill = skills.get(item.skill_id)
            if not user or not user.vk_user_id or not skill:
                continue
            days_left = (item.planned_date - today).days
            text = (
                f"Напоминание: подтверждение навыка **{skill.name}** запланировано "
                f"на {item.planned_date.isoformat()} "
                f"({'сегодня' if days_left == 0 else f'через {days_left} дн.'})."
            )
            sent = await vk_notify.send_message(user.vk_user_id, text)
            if sent:
                item.reminder_sent_at = today
        await db.commit()


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_upcoming_plan_dates,
        "interval",
        hours=settings.vk_reminder_check_interval_hours,
        id="vk_plan_reminders",
        next_run_time=datetime.datetime.now(),
    )
    scheduler.start()
    logger.info("VK reminder scheduler started (every %sh)", settings.vk_reminder_check_interval_hours)
    return scheduler
