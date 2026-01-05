from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = DATA_DIR / "assets"
EXPORTS_DIR = BASE_DIR / "exports"

ASSETS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

SAFE_ZONES = {
    # margins in pixels for each format: top, right, bottom, left
    "FB_STORY": (250, 50, 250, 50),
    "IG_STORY": (250, 50, 250, 50),
    "SQUARE": (150, 150, 150, 150),
    "LANDSCAPE": (200, 200, 200, 200),
    "CHECKOUT": (200, 200, 200, 200),
}

FORMATS = {
    # width, height
    "FB_STORY": (1080, 1920),
    "IG_STORY": (1080, 1920),
    "SQUARE": (1080, 1080),
    "LANDSCAPE": (1200, 628),
    "CHECKOUT": (1200, 900),
}

# Minimal starting list; can be expanded
BANNED_COPY_PATTERNS = [
    r"\bfree\b",
    r"\bwin\b|\bcompetition\b|\bcontest\b",
    r"\bprice\b|\b£\s*\d|\d+\.\d{2}",
    r"\bsustainable\b|\beco\b|\bgreen\b|\benvironment\b",
    r"\bclinically\s+proven\b|\bguarantee\b",
]

DRINKAWARE_TEXT = "Drinkaware.co.uk"
MIN_FONT_SIZES = {
    "headline": 48,
    "subhead": 28,
    "value": 36,
    "drinkaware": 18,
}
