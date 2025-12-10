from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.models import UserCreate, UserRead, User
from src.backend import deps
from src.repositories.user import user_repo

router = APIRouter()


@router.post("/user/", response_model=UserRead)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    _current_user: User = Depends(
        deps.get_current_active_superuser
    ),  # 403 if not superuser
) -> User:
    """Creates a new user, a function restricted to superusers,
    and prevents the creation of users with duplicate email addresses."""
    return user_repo.register(db=db, obj_in=user_in)
