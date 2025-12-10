from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.models import Item, ItemRead, ItemCreate, ItemUpdate, User
from src.backend import deps
from src.repositories.item import item_repo

router = APIRouter()


@router.get("/items/", response_model=List[ItemRead])
def read_items(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> List[Item]:
    """Retrieves items for the current user."""
    return item_repo.get_for_user(db=db, current_user=current_user)


@router.post("/item/", response_model=ItemRead)
def create_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: ItemCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Item:
    """Creates a new item for the current user."""
    return item_repo.create_for_user(db=db, obj_in=item_in, current_user=current_user)


@router.put("/item/{item_id}", response_model=ItemRead)
def update_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    item_in: ItemUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Item:
    """Update an item after verifying ownership."""
    return item_repo.update_for_user(
        db=db, item_id=item_id, obj_in=item_in, current_user=current_user
    )


@router.delete("/item/{item_id}", response_model=ItemRead)
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Item:
    """Delete an item after verifying ownership."""
    return item_repo.delete_for_user(db=db, item_id=item_id, current_user=current_user)
