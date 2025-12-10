from typing import Any
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from src.core import security
from src.repositories.user import user_repo
from src.db.session import get_db

router = APIRouter()


@router.post("/login/access-token")
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Authenticates a user via form data and returns a bearer access token upon success."""
    user = user_repo.authenticate(
        db=db, email=form_data.username, password=form_data.password
    )
    return {
        "access_token": security.create_access_token(user.id),
        "token_type": "bearer",
    }
