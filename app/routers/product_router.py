from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product_schema import ProductCreateRequest, ProductListResponse, ProductResponse, ProductUpdateRequest
from app.services.auth_service import get_current_user
from app.services.file_service import save_product_image
from app.services.product_service import ProductService

router = APIRouter(prefix='/products', tags=['Products'])


@router.get('', response_model=ProductListResponse)
def list_products(
    search: str | None = Query(default=None),
    typeMaterial: str | None = Query(default=None),
    breed: str | None = Query(default=None),
    origin: str | None = Query(default=None),
    location: str | None = Query(default=None),
    priceMax: float | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    items = service.list_products(
        search=search,
        type_material=typeMaterial,
        breed=breed,
        origin=origin,
        location=location,
        price_max=priceMax,
    )
    return ProductListResponse(total=len(items), items=items)


@router.get('/me/list', response_model=ProductListResponse)
def list_my_products(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = ProductService(db)
    items = service.list_my_products(current_user)
    return ProductListResponse(total=len(items), items=items)


@router.get('/{product_id}', response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return ProductService(db).get_product(product_id)


@router.post('', response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(...),
    typeMaterial: str = Form(...),
    breed: str = Form(...),
    origin: str = Form('Nacional'),
    location: str = Form(...),
    price: float = Form(...),
    availability: str = Form('Disponible'),
    seller: str | None = Form(None),
    image: str | None = Form(None),
    description: str = Form(...),
    pedigree: str | None = Form(None),
    notes: str | None = Form(None),
    certifications: str | None = Form(None),
    imageFile: UploadFile | None = File(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uploaded_image_url = await save_product_image(imageFile)

    payload = ProductCreateRequest(
        name=name,
        typeMaterial=typeMaterial,
        breed=breed,
        origin=origin,
        location=location,
        price=price,
        availability=availability,
        seller=seller,
        image=uploaded_image_url or image,
        description=description,
        pedigree=pedigree,
        notes=notes,
        certifications=certifications,
    )

    return ProductService(db).create_product(payload, current_user)


@router.put('/{product_id}', response_model=ProductResponse)
async def update_product(
    product_id: int,
    name: str | None = Form(None),
    typeMaterial: str | None = Form(None),
    breed: str | None = Form(None),
    origin: str | None = Form(None),
    location: str | None = Form(None),
    price: float | None = Form(None),
    availability: str | None = Form(None),
    seller: str | None = Form(None),
    image: str | None = Form(None),
    description: str | None = Form(None),
    pedigree: str | None = Form(None),
    notes: str | None = Form(None),
    certifications: str | None = Form(None),
    status_value: str | None = Form(None, alias='status'),
    imageFile: UploadFile | None = File(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uploaded_image_url = await save_product_image(imageFile)

    payload = ProductUpdateRequest(
        name=name,
        typeMaterial=typeMaterial,
        breed=breed,
        origin=origin,
        location=location,
        price=price,
        availability=availability,
        seller=seller,
        image=uploaded_image_url or image,
        description=description,
        pedigree=pedigree,
        notes=notes,
        certifications=certifications,
        status=status_value,
    )

    return ProductService(db).update_product(product_id, payload, current_user)


@router.delete('/{product_id}')
def delete_product(product_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return ProductService(db).delete_product(product_id, current_user)
