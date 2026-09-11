from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, permissions, schemas
from ..database import get_db
from ..deps import get_current_user
from ..ids import new_id

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[schemas.PlanItemOut])
async def list_plans(db: AsyncSession = Depends(get_db), _user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.PlanItem))
    return [schemas.PlanItemOut.from_orm_item(item) for item in result.scalars().all()]


async def _require_can_manage(db: AsyncSession, user: models.User, target_user_id: str) -> None:
    if not await permissions.can_manage(db, user, target_user_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав для управления планом этого сотрудника")


@router.post("", response_model=schemas.PlanItemOut, status_code=status.HTTP_201_CREATED)
async def add_skill_to_plan(
    payload: schemas.PlanItemCreate,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    await _require_can_manage(db, user, payload.user_id)
    existing = await db.execute(
        select(models.PlanItem).where(
            models.PlanItem.user_id == payload.user_id, models.PlanItem.skill_id == payload.skill_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Этот навык уже есть в плане сотрудника")

    item = models.PlanItem(
        id=new_id("plan"), user_id=payload.user_id, skill_id=payload.skill_id, planned_date=payload.planned_date
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return schemas.PlanItemOut.from_orm_item(item)


@router.patch("/{item_id}", response_model=schemas.PlanItemOut)
async def update_planned_date(
    item_id: str,
    payload: schemas.PlanItemUpdate,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    item = await db.get(models.PlanItem, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пункт плана не найден")
    await _require_can_manage(db, user, item.user_id)
    item.planned_date = payload.planned_date
    await db.commit()
    await db.refresh(item)
    return schemas.PlanItemOut.from_orm_item(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_plan_item(
    item_id: str, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)
):
    item = await db.get(models.PlanItem, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пункт плана не найден")
    await _require_can_manage(db, user, item.user_id)
    await db.delete(item)
    await db.commit()
