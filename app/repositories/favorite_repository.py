from sqlalchemy.orm import Session, joinedload

from app.models.favorite_model import Favorite
from app.models.product_model import Product


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: int):
        return (
            self.db.query(Favorite)
            .options(joinedload(Favorite.product).joinedload(Product.seller), joinedload(Favorite.product).joinedload(Product.certifications))
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .all()
        )

    def get_by_user_and_product(self, user_id: int, product_id: int):
        return self.db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.product_id == product_id).first()

    def create(self, user_id: int, product_id: int):
        favorite = Favorite(user_id=user_id, product_id=product_id)
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite

    def delete(self, favorite: Favorite):
        self.db.delete(favorite)
        self.db.commit()
