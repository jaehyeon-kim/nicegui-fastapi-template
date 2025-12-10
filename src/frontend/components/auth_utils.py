from sqlmodel import Session
from fastapi import HTTPException
from src.backend.deps import get_user_from_token
from src.models import User
from src.frontend import state


def get_current_user_from_state(db: Session) -> User:
    """Helper to get the current user from the token stored in UI state."""
    token_with_bearer = state.get_token()
    if not token_with_bearer:
        raise HTTPException(status_code=401, detail="Authentication token not found.")
    token = token_with_bearer.split(" ")[1]
    return get_user_from_token(db=db, token=token)
