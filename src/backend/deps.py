from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlmodel import Session

from src.core import security
from src.core.config import settings
from src.db.session import get_db
from src.models import models

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")


def get_user_from_token(db: Session, token: str) -> models.User:
    """
    Decodes a JWT token and returns the corresponding user from the database.
    This function does NOT use Depends() and can be called from anywhere.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = payload.get("sub")
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = db.get(models.User, int(token_data))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    """
    FastAPI dependency that gets the current user from the token.
    It simply calls our reusable core logic function.
    """
    return get_user_from_token(db=db, token=token)


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """A dependency function that verifies if the current user has superuser privileges."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
