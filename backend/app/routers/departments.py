from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user, require_admin
from ..ids import new_id

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[schemas.DepartmentOut])
async def list_departments(db: AsyncSession = Depends(get_db), _user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Department))
    return result.scalars().all()


async def _descendant_ids(db: AsyncSession, dept_id: str) -> set[str]:
    result = await db.execute(select(models.Department))
    all_depts = result.scalars().all()
    children_of: dict[str, list[str]] = {}
    for d in all_depts:
        if d.parent_id:
            children_of.setdefault(d.parent_id, []).append(d.id)

    descendants: set[str] = set()
    stack = list(children_of.get(dept_id, []))
    while stack:
        current = stack.pop()
        if current in descendants:
            continue
        descendants.add(current)
        stack.extend(children_of.get(current, []))
    return descendants


@router.post("", response_model=schemas.DepartmentOut, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: schemas.DepartmentCreate, db: AsyncSession = Depends(get_db), _admin: models.User = Depends(require_admin)
):
    dept = models.Department(id=new_id("dept"), name=payload.name, parent_id=payload.parent_id, manager_id=payload.manager_id)
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


@router.patch("/{dept_id}", response_model=schemas.DepartmentOut)
async def update_department(
    dept_id: str,
    payload: schemas.DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    dept = await db.get(models.Department, dept_id)
    if not dept:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Подразделение не найдено")
    data = payload.model_dump(exclude_unset=True)
    if "parent_id" in data and data["parent_id"] is not None:
        if data["parent_id"] == dept_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Подразделение не может быть родителем самого себя")
        if data["parent_id"] in await _descendant_ids(db, dept_id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нельзя перенести подразделение в собственное поддерево")
    for field, value in data.items():
        setattr(dept, field, value)
    await db.commit()
    await db.refresh(dept)
    return dept


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    dept_id: str, db: AsyncSession = Depends(get_db), _admin: models.User = Depends(require_admin)
):
    dept = await db.get(models.Department, dept_id)
    if not dept:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Подразделение не найдено")
    await db.delete(dept)
    await db.commit()
