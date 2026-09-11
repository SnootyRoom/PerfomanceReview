from contextlib import asynccontextmanager

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def translate_integrity_error(db: AsyncSession, message: str):
    """Rolls back and raises a friendly 409 if the wrapped DB write violates
    a foreign key (e.g. deleting a skill/direction/user still referenced
    elsewhere)."""
    try:
        yield
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, message) from None
