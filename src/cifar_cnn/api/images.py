"""Image input validation — reject oversized, wrong type, or non-CIFAR dimensions."""

from __future__ import annotations

import io

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from cifar_cnn.api.config import Settings

ALLOWED_CONTENT_TYPES = frozenset({"image/png", "image/jpeg", "image/jpg"})
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"
EXPECTED_SIZE = (32, 32)
# Bound decompression work for untrusted uploads (CIFAR is 32x32).
Image.MAX_IMAGE_PIXELS = 1_000_000


async def read_and_validate_image(
    upload: UploadFile,
    settings: Settings,
) -> tuple[Image.Image, int, str]:
    content_type = (upload.content_type or "").lower().strip()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="unsupported_media_type",
        )

    raw = await upload.read(settings.max_upload_bytes + 1)
    byte_length = len(raw)
    if byte_length == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="empty_image",
        )
    if byte_length > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="payload_too_large",
        )

    if content_type in {"image/png"} and not raw.startswith(PNG_MAGIC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_image_magic",
        )
    if content_type in {"image/jpeg", "image/jpg"} and not raw.startswith(JPEG_MAGIC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_image_magic",
        )

    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_image",
        ) from exc

    if img.size != EXPECTED_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_dimensions",
        )
    if img.mode not in {"RGB", "L"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_image_mode",
        )
    rgb: Image.Image = img.convert("RGB") if img.mode != "RGB" else img
    return rgb, byte_length, content_type
