from typing import Optional, Union, Dict, Any
from sqlmodel import Session, select
from backend.models.models import Item, ItemCreate, ItemUpdate


class ItemRepository:
    def get(self, db: Session, id: int) -> Optional[Item]:
        return db.get(Item, id)

    def get_by_title_and_owner(
        self, db: Session, *, title: str, owner_id: int
    ) -> Optional[Item]:
        return db.exec(
            select(Item).where(Item.title == title, Item.owner_id == owner_id)
        ).first()

    def create_with_owner(
        self, db: Session, *, obj_in: ItemCreate, owner_id: int
    ) -> Item:
        db_obj = Item(**obj_in.dict(), owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ):
        return db.exec(
            select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
        ).all()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100):
        return db.exec(select(Item).offset(skip).limit(limit)).all()

    def update(
        self, db: Session, *, db_obj: Item, obj_in: Union[ItemUpdate, Dict[str, Any]]
    ) -> Item:
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
        obj = db.get(Item, id)
        db.delete(obj)
        db.commit()
        return obj


item_repo = ItemRepository()
