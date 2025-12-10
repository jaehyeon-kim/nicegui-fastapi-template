from typing import Optional, List
from fastapi import HTTPException
from sqlmodel import Session, select
from src.models.models import Item, ItemCreate, ItemUpdate, User


class ItemRepository:
    def get_for_user(self, db: Session, *, current_user: User) -> List[Item]:
        """
        Retrieves all items for a superuser, or only items belonging to a normal user.
        """
        if current_user.is_superuser:
            return self.get_multi(db)
        else:
            return self.get_multi_by_owner(db, owner_id=current_user.id)

    def create_for_user(
        self, db: Session, *, obj_in: ItemCreate, current_user: User
    ) -> Item:
        """
        Creates a new item for the current user, first checking for duplicate titles.
        """
        existing_item = self.get_by_title_and_owner(
            db=db, title=obj_in.title, owner_id=current_user.id
        )
        if existing_item:
            raise HTTPException(
                status_code=409,
                detail="An item with this title already exists.",
            )
        try:
            item = item_repo.create(db=db, obj_in=obj_in, owner_id=current_user.id)
            return item
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while creating the item.",
            )

    def update_for_user(
        self,
        db: Session,
        *,
        item_id: int,
        obj_in: ItemUpdate,
        current_user: User,
    ) -> Item:
        """
        Updates an item for the current user, first checking for permissions.
        """
        item_to_update = self.get_with_permission(
            db=db, id=item_id, current_user=current_user
        )
        item = self.update(db=db, db_obj=item_to_update, obj_in=obj_in)
        return item

    def delete_for_user(self, db: Session, *, item_id: int, current_user: User):
        """
        Deletes an item for the current user, first checking for permissions.
        """
        item_to_delete = self.get_with_permission(
            db=db, id=item_id, current_user=current_user
        )
        item = item_repo.remove(db=db, id=item_to_delete.id)
        return item

    def get(self, db: Session, id: int) -> Optional[Item]:
        """Retrieves a single item from the database by its primary key ID."""
        return db.get(Item, id)

    def get_with_permission(self, db: Session, *, id: int, current_user: User) -> Item:
        """Retrieves an item by ID and verifies the current user has permission (is owner or superuser)."""
        item = self.get(db, id=id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not current_user.is_superuser and (item.owner_id != current_user.id):
            raise HTTPException(status_code=403, detail="Insufficient permission")
        return item

    def get_by_title_and_owner(
        self, db: Session, *, title: str, owner_id: int
    ) -> Optional[Item]:
        """Fetches an item based on its title and the ID of its owner."""
        return db.exec(
            select(Item).where(Item.title == title, Item.owner_id == owner_id)
        ).first()

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Item]:
        """Retrieves all items associated with a specific owner, with options for pagination."""
        return db.exec(
            select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
        ).all()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Item]:
        """Retrieves a list of all items, with options for pagination."""
        return db.exec(select(Item).offset(skip).limit(limit)).all()

    def create(self, db: Session, *, obj_in: ItemCreate, owner_id: int) -> Item:
        """Creates a new item in the database, assigning it to a specific owner."""
        db_obj = Item(**obj_in.dict(), owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Item, obj_in: ItemUpdate) -> Item:
        """Updates the attributes of an existing item in the database."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Item:
        """Deletes a specific item from the database by its ID."""
        obj = db.get(Item, id)
        db.delete(obj)
        db.commit()
        return obj


item_repo = ItemRepository()
