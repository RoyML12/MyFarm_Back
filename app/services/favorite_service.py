from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService


class FavoriteService:
    def __init__(self, db: Session):
        self.favorite_repo = FavoriteRepository(db)
        self.product_repo = ProductRepository(db)

    def list_favorites(self, current_user):
        favorites = self.favorite_repo.list_by_user(current_user.id)
        items = [ProductService.serialize_product(item.product) for item in favorites if item.product and item.product.status != 'deleted']
        return {'total': len(items), 'items': items}

    def add_favorite(self, product_id: int, current_user):
        product = self.product_repo.get_by_id(product_id)
        if not product or product.status == 'deleted':
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Producto no encontrado')
        exists = self.favorite_repo.get_by_user_and_product(current_user.id, product_id)
        if exists:
            return {'message': 'El producto ya estaba en favoritos'}
        self.favorite_repo.create(current_user.id, product_id)
        return {'message': 'Producto agregado a favoritos'}

    def remove_favorite(self, product_id: int, current_user):
        favorite = self.favorite_repo.get_by_user_and_product(current_user.id, product_id)
        if not favorite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Favorito no encontrado')
        self.favorite_repo.delete(favorite)
        return {'message': 'Producto eliminado de favoritos'}
