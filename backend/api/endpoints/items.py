from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend import models
from backend.api import deps
from backend.repositories.item import item_repo

router = APIRouter()


@router.get("/items/", response_model=List[models.ItemRead])
def read_items(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    if current_user.is_superuser:
        items = item_repo.get_multi(db)
    else:
        items = item_repo.get_multi_by_owner(db, owner_id=current_user.id)
    return items


@router.post("/item/", response_model=models.ItemRead)
def create_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: models.ItemCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    existing_item = item_repo.get_by_title_and_owner(
        db=db, title=item_in.title, owner_id=current_user.id
    )
    if existing_item:
        raise HTTPException(
            status_code=409,
            detail="An item with this title already exists.",
        )

    try:
        item = item_repo.create_with_owner(
            db=db, obj_in=item_in, owner_id=current_user.id
        )
        return item
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while creating the item.",
        )


@router.put("/item/{item_id}", response_model=models.ItemRead)
def update_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    item_in: models.ItemUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update an item.
    """
    item = item_repo.get(db=db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    item = item_repo.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.delete("/item/{item_id}", response_model=models.ItemRead)
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete an item.
    """
    item = item_repo.get(db=db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    item = item_repo.remove(db=db, id=item_id)
    return item
