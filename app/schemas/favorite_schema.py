from typing import List

from pydantic import BaseModel

from app.schemas.product_schema import ProductResponse


class FavoriteListResponse(BaseModel):
    total: int
    items: List[ProductResponse]
