from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import models
from backend.database.session import get_db
from backend.auth.dependencies import get_current_user
from typing import List
from pydantic import BaseModel

router = APIRouter(
    prefix="/favorite-users",
    tags=["favorite-users"],
)

class FavoriteUserCreate(BaseModel):
    username: str

class FavoriteUserOut(BaseModel):
    id: int
    username: str

@router.post("/", response_model=FavoriteUserOut)
def add_favorite_user(data: FavoriteUserCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    fav_user = models.FavoriteUser(username=data.username, owner_id=user.id)
    db.add(fav_user)
    db.commit()
    db.refresh(fav_user)
    return fav_user

@router.get("/", response_model=List[FavoriteUserOut])
def list_favorite_users(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.FavoriteUser).filter_by(owner_id=user.id).all()

@router.delete("/{fav_user_id}", response_model=dict)
def delete_favorite_user(fav_user_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    fav_user = db.query(models.FavoriteUser).filter_by(id=fav_user_id, owner_id=user.id).first()
    if not fav_user:
        raise HTTPException(status_code=404, detail="お気に入りユーザーが見つかりません")
    db.delete(fav_user)
    db.commit()
    return {"success": True}