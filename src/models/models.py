from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

from src.core.config import settings

TABLE_ARGS = {"schema": settings.SCHEMA_NAME}


class UserBase(SQLModel):
    """Establishes the fundamental fields common to all user-related models,
    such as email, is_active, is_superuser, and full_name."""

    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Inherits from UserBase and is used specifically for creating new users.
    It adds a password field that is required only during the user creation process."""

    password: str = Field(min_length=8, max_length=72)


class User(UserBase, table=True):
    """This is the primary database table model for a user.
    It includes all fields from UserBase plus the database-specific fields: id (the primary key) and hashed_password.
    It also defines the one-to-many relationship, indicating that a user can own multiple items."""

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")

    __table_args__ = TABLE_ARGS


class UserRead(UserBase):
    """Designed for API responses when retrieving user data.
    It includes the user's id but omits sensitive information like the hashed_password to prevent it from being exposed."""

    id: int


class ItemBase(SQLModel):
    """The base model for items, containing the core fields: title and description."""

    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    """Inherits from ItemBase and is used for validating the data when a new item is created."""

    pass


class ItemUpdate(SQLModel):
    """Used for updating an existing item. Its fields (title, description) are optional,
    allowing for partial updates where only the changed fields need to be provided."""

    title: Optional[str] = None
    description: Optional[str] = None


class Item(ItemBase, table=True):
    """The database table model for an item. It includes the ItemBase fields along with an id (primary key) and an owner_id,
    which is a foreign key linking the item to a user. It also defines the relationship back to the User model."""

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
    """The model for returning item data in API responses, including the item's id and the owner_id."""

    id: int
    owner_id: int
