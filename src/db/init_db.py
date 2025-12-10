from sqlmodel import Session, SQLModel
from src.core.config import settings
from src.repositories.user import user_repo
from src.models import models
from src.db.session import engine


def init() -> None:
    """Initializes the database, creating all necessary tables
    and ensuring the first superuser account is created."""
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        user = user_repo.get_by_email(db=session, email=settings.FIRST_SUPERUSER)
        if not user:
            user_in = models.UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user_repo.create(db=session, obj_in=user_in)
