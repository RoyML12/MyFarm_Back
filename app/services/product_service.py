from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import ProductResponse


class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    @staticmethod
    def normalize_certifications(certifications):
        if certifications is None:
            return []
        if isinstance(certifications, str):
            return [item.strip() for item in certifications.split(',') if item.strip()]
        if isinstance(certifications, list):
            return [str(item).strip() for item in certifications if str(item).strip()]
        return []

    @staticmethod
    def serialize_product(product) -> ProductResponse:
        return ProductResponse(
            id=product.id,
            sellerId=product.seller_id,
            seller=product.seller.full_name if product.seller else 'Sin vendedor',
            name=product.name,
            typeMaterial=product.type_material,
            breed=product.breed,
            origin=product.origin,
            location=product.location,
            price=float(product.price),
            availability=product.availability,
            image=product.image_url,
            description=product.description,
            pedigree=product.pedigree,
            notes=product.notes,
            certifications=[item.certification_name for item in product.certifications],
            status=product.status,
            createdAt=product.created_at,
            updatedAt=product.updated_at,
        )

    def list_products(self, **filters):
        return [self.serialize_product(item) for item in self.repo.list_products(**filters)]

    def list_my_products(self, current_user):
        return [self.serialize_product(item) for item in self.repo.list_by_seller(current_user.id)]

    def get_product(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Producto no encontrado')
        return self.serialize_product(product)

    def create_product(self, payload, current_user):
        data = {
            'seller_id': current_user.id,
            'name': payload.name.strip(),
            'type_material': payload.typeMaterial,
            'breed': payload.breed.strip(),
            'origin': payload.origin,
            'location': payload.location.strip(),
            'price': payload.price,
            'availability': payload.availability,
            'image_url': payload.image.strip() if payload.image else None,
            'description': payload.description.strip(),
            'pedigree': payload.pedigree.strip() if payload.pedigree else None,
            'notes': payload.notes.strip() if payload.notes else None,
            'status': 'active',
            'certifications': self.normalize_certifications(payload.certifications),
        }
        product = self.repo.create_product(data)
        return self.serialize_product(product)

    def update_product(self, product_id: int, payload, current_user):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Producto no encontrado')
        if product.seller_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No puedes editar este producto')

        data = {}
        if payload.name is not None:
            data['name'] = payload.name.strip()
        if payload.typeMaterial is not None:
            data['type_material'] = payload.typeMaterial
        if payload.breed is not None:
            data['breed'] = payload.breed.strip()
        if payload.origin is not None:
            data['origin'] = payload.origin
        if payload.location is not None:
            data['location'] = payload.location.strip()
        if payload.price is not None:
            data['price'] = payload.price
        if payload.availability is not None:
            data['availability'] = payload.availability
        if payload.image is not None:
            data['image_url'] = payload.image.strip() if payload.image else None
        if payload.description is not None:
            data['description'] = payload.description.strip()
        if payload.pedigree is not None:
            data['pedigree'] = payload.pedigree.strip() if payload.pedigree else None
        if payload.notes is not None:
            data['notes'] = payload.notes.strip() if payload.notes else None
        if payload.status is not None:
            data['status'] = payload.status
        if payload.certifications is not None:
            data['certifications'] = self.normalize_certifications(payload.certifications)

        updated = self.repo.update_product(product, data)
        return self.serialize_product(updated)

    def delete_product(self, product_id: int, current_user):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Producto no encontrado')
        if product.seller_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No puedes eliminar este producto')
        self.repo.soft_delete(product)
        return {'message': 'Producto eliminado correctamente'}
