from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .database import get_db
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> models.User:
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, "Не авторизован")
    if not token:
        raise unauthorized
    user_id = decode_access_token(token)
    if not user_id:
        raise unauthorized
    user = await db.get(models.User, user_id)
    if not user:
        raise unauthorized
    return user


async def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Требуются права администратора")
    return user
