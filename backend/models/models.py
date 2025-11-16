from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

from backend.core.config import settings

TABLE_ARGS = {"schema": settings.SCHEMA_NAME}


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")

    __table_args__ = TABLE_ARGS


class UserRead(UserBase):
    id: int


class ItemBase(SQLModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    owner_id: Optional[int] = Field(
        default=None, foreign_key=f"{settings.SCHEMA_NAME}.user.id"
    )
    owner: Optional["User"] = Relationship(
        back_populates="items", sa_relationship_kwargs={"foreign_keys": "Item.owner_id"}
    )

    __table_args__ = TABLE_ARGS


class ItemRead(ItemBase):
    id: int
    owner_id: int
