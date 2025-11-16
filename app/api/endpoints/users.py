from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app import models
from app.api import deps
from app.repositories.user import user_repo

router = APIRouter()


@router.post("/users/", response_model=models.UserRead)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: models.UserCreate,
    _current_user: models.User = Depends(
        deps.get_current_active_superuser
    ),  # 403 if not superuser
) -> Any:
    user = user_repo.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = user_repo.create(db, obj_in=user_in)
    return user
