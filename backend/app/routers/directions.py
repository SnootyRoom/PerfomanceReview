from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user, require_admin
from ..errors import translate_integrity_error
from ..ids import new_id

router = APIRouter(prefix="/directions", tags=["directions"])


@router.get("", response_model=list[schemas.DirectionOut])
async def list_directions(db: AsyncSession = Depends(get_db), _user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Direction))
    return result.scalars().all()


@router.post("", response_model=schemas.DirectionOut, status_code=status.HTTP_201_CREATED)
async def create_direction(
    payload: schemas.DirectionCreate, db: AsyncSession = Depends(get_db), _admin: models.User = Depends(require_admin)
):
    direction = models.Direction(id=new_id("dir"), name=payload.name)
    db.add(direction)
    await db.commit()
    await db.refresh(direction)
    return direction


@router.patch("/{direction_id}", response_model=schemas.DirectionOut)
async def rename_direction(
    direction_id: str,
    payload: schemas.DirectionUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    direction = await db.get(models.Direction, direction_id)
    if not direction:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Направление не найдено")
    direction.name = payload.name
    await db.commit()
    await db.refresh(direction)
    return direction


@router.delete("/{direction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_direction(
    direction_id: str, db: AsyncSession = Depends(get_db), _admin: models.User = Depends(require_admin)
):
    direction = await db.get(models.Direction, direction_id)
    if not direction:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Направление не найдено")
    async with translate_integrity_error(db, "Сначала удалите или перенесите навыки этого направления"):
        await db.delete(direction)
        await db.commit()
