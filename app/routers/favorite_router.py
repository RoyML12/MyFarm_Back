from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.favorite_schema import FavoriteListResponse
from app.services.auth_service import get_current_user
from app.services.favorite_service import FavoriteService

router = APIRouter(prefix='/favorites', tags=['Favorites'])


@router.get('', response_model=FavoriteListResponse)
def list_favorites(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return FavoriteService(db).list_favorites(current_user)


@router.post('/{product_id}')
def add_favorite(product_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return FavoriteService(db).add_favorite(product_id, current_user)


@router.delete('/{product_id}')
def remove_favorite(product_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return FavoriteService(db).remove_favorite(product_id, current_user)
