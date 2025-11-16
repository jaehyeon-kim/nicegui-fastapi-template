from typing import Optional
from sqlmodel import Session, select
from backend.core.security import get_password_hash, verify_password
from backend.models.models import User, UserCreate


class UserRepository:
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.exec(select(User).where(User.email == email)).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user


user_repo = UserRepository()
