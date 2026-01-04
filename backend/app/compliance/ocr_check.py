from __future__ import annotations

from PIL import Image, ImageOps
import io


def ocr_text_from_bytes(image_bytes: bytes) -> str:
    """Extracts text (lowercased) from image bytes with light preprocessing."""
    try:
        try:
            import pytesseract  # type: ignore
        except Exception:
            return ""

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        gray = ImageOps.grayscale(img)
        gray = ImageOps.autocontrast(gray, cutoff=2)
        # If the Tesseract binary isn't installed/configured, this may throw.
        text = pytesseract.image_to_string(gray, lang="eng")
        return text.strip().lower()
    except Exception:
        return ""
