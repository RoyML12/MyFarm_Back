from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    typeMaterial: str = Field(min_length=2, max_length=50)
    breed: str = Field(min_length=2, max_length=100)
    origin: str = 'Nacional'
    location: str = Field(min_length=2, max_length=150)
    price: float = Field(gt=0)
    availability: str = 'Disponible'
    seller: Optional[str] = None
    image: Optional[str] = None
    description: str = Field(min_length=5)
    pedigree: Optional[str] = None
    notes: Optional[str] = None
    certifications: Optional[Union[str, List[str]]] = None


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    typeMaterial: Optional[str] = None
    breed: Optional[str] = None
    origin: Optional[str] = None
    location: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    availability: Optional[str] = None
    seller: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    pedigree: Optional[str] = None
    notes: Optional[str] = None
    certifications: Optional[Union[str, List[str]]] = None
    status: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    sellerId: int
    seller: str
    name: str
    typeMaterial: str
    breed: str
    origin: str
    location: str
    price: float
    availability: str
    image: Optional[str] = None
    description: str
    pedigree: Optional[str] = None
    notes: Optional[str] = None
    certifications: List[str] = []
    status: str
    createdAt: datetime
    updatedAt: datetime


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]
