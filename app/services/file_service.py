from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOADS_DIR = BASE_DIR / "uploads"
PRODUCT_UPLOADS_DIR = UPLOADS_DIR / "products"
PRODUCT_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


async def save_product_image(image: UploadFile | None) -> str | None:
    if image is None or not image.filename:
        return None

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de imagen no permitido. Usa JPG, PNG o WEBP.",
        )

    content = await image.read()

    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen no debe pesar más de 5 MB.",
        )

    extension = ALLOWED_IMAGE_TYPES[image.content_type]
    filename = f"{uuid4().hex}{extension}"
    file_path = PRODUCT_UPLOADS_DIR / filename

    file_path.write_bytes(content)

    return f"uploads/products/{filename}"
