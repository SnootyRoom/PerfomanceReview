from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user, require_admin
from ..errors import translate_integrity_error
from ..ids import new_id

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[schemas.SkillOut])
async def list_skills(db: AsyncSession = Depends(get_db), _user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Skill))
    return result.scalars().all()


@router.post("", response_model=schemas.SkillOut, status_code=status.HTTP_201_CREATED)
async def create_skill(
    payload: schemas.SkillCreate, db: AsyncSession = Depends(get_db), _admin: models.User = Depends(require_admin)
):
    skill = models.Skill(id=new_id("skill"), name=payload.name, direction_id=payload.direction_id)
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.patch("/{skill_id}", response_model=schemas.SkillOut)
async def update_skill(
    skill_id: str,
    payload: schemas.SkillUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    skill = await db.get(models.Skill, skill_id)
    if not skill:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Навык не найден")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(skill, field, value)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: str, db: AsyncSession = Depends(get_db), _admin: models.User = Depends(require_admin)
):
    skill = await db.get(models.Skill, skill_id)
    if not skill:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Навык не найден")
    async with translate_integrity_error(
        db, "Навык используется в планах обучения или протоколах встреч — сначала уберите его оттуда"
    ):
        await db.delete(skill)
        await db.commit()
