from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.product_certification_model import ProductCertification
from app.models.product_model import Product
from app.models.user_model import User


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_products(self, *, search=None, type_material=None, breed=None, origin=None, location=None, price_max=None, include_inactive=False):
        query = self.db.query(Product).options(joinedload(Product.seller), joinedload(Product.certifications))

        if not include_inactive:
            query = query.filter(Product.status == 'active')

        if search:
            search_like = f'%{search.strip()}%'
            query = query.join(User, Product.seller_id == User.id).filter(
                or_(Product.name.ilike(search_like), Product.breed.ilike(search_like), User.full_name.ilike(search_like))
            )

        if type_material and type_material != 'all':
            query = query.filter(Product.type_material == type_material)
        if breed and breed != 'all':
            query = query.filter(Product.breed == breed)
        if origin and origin != 'all':
            query = query.filter(Product.origin == origin)
        if location and location != 'all':
            query = query.filter(Product.location == location)
        if price_max not in (None, ''):
            query = query.filter(Product.price <= float(price_max))

        return query.order_by(Product.updated_at.desc(), Product.id.desc()).all()

    def list_by_seller(self, seller_id: int):
        return (
            self.db.query(Product)
            .options(joinedload(Product.seller), joinedload(Product.certifications))
            .filter(Product.seller_id == seller_id, Product.status != 'deleted')
            .order_by(Product.updated_at.desc(), Product.id.desc())
            .all()
        )

    def get_by_id(self, product_id: int):
        return (
            self.db.query(Product)
            .options(joinedload(Product.seller), joinedload(Product.certifications))
            .filter(Product.id == product_id, Product.status != 'deleted')
            .first()
        )

    def create_product(self, data: dict):
        certifications = data.pop('certifications', [])
        product = Product(**data)
        self.db.add(product)
        self.db.flush()

        self.replace_certifications(product, certifications)
        self.db.commit()
        self.db.refresh(product)
        return self.get_by_id(product.id)

    def update_product(self, product: Product, data: dict):
        certifications = data.pop('certifications', None)
        for key, value in data.items():
            setattr(product, key, value)

        if certifications is not None:
            self.replace_certifications(product, certifications)

        self.db.commit()
        self.db.refresh(product)
        return self.get_by_id(product.id)

    def soft_delete(self, product: Product):
        product.status = 'deleted'
        self.db.commit()
        self.db.refresh(product)
        return product

    def replace_certifications(self, product: Product, certifications: list[str]):
        self.db.query(ProductCertification).filter(ProductCertification.product_id == product.id).delete()
        for name in certifications:
            cert = ProductCertification(product_id=product.id, certification_name=name)
            self.db.add(cert)
