"""Safe image validation, dimensions clamping and preprocessing for OCR (Phase 8)."""

import io
from typing import Tuple
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from app.core.logging import logger
from app.ingestion.limits import limits


class ImagePreprocessor:
    """Safely decodes and prepares images for robust optical character recognition."""

    @staticmethod
    def validate_and_load(image_bytes: bytes) -> Image.Image:
        """Validate format, prevent decompression bomb, and decode image."""
        if not image_bytes:
            raise ValueError("Image byte buffer is empty.")

        if len(image_bytes) > limits.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"Image exceeds maximum size limit of {limits.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB.")

        try:
            # Prevent decompression bomb attacks
            Image.MAX_IMAGE_PIXELS = limits.MAX_IMAGE_PIXELS
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()  # Verify integrity
            
            # Reopen after verify
            img = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.warning(f"Image decode failed: {e}")
            raise ValueError(f"Invalid or corrupted image format: {e}")

        # Check dimensions
        width, height = img.size
        if width > limits.MAX_IMAGE_WIDTH or height > limits.MAX_IMAGE_HEIGHT:
            logger.info(f"Resizing oversized image from {width}x{height} to fit within {limits.MAX_IMAGE_WIDTH}x{limits.MAX_IMAGE_HEIGHT}")
            img.thumbnail((limits.MAX_IMAGE_WIDTH, limits.MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)

        return img

    @staticmethod
    def enhance_for_ocr(img: Image.Image) -> Image.Image:
        """Convert to high-contrast grayscale to improve OCR token extraction."""
        # Convert to Grayscale
        if img.mode != "L":
            img = img.convert("L")

        # Autocontrast
        img = ImageOps.autocontrast(img)

        # Slight sharpening
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)

        return img


image_preprocessor = ImagePreprocessor()
