from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Format(str, Enum):
    FB_STORY = "FB_STORY"
    IG_STORY = "IG_STORY"
    SQUARE = "SQUARE"
    LANDSCAPE = "LANDSCAPE"
    CHECKOUT = "CHECKOUT"

class RGBA(BaseModel):
    r: int = 0
    g: int = 0
    b: int = 0
    a: float = 1.0

class Rect(BaseModel):
    x: int
    y: int
    width: int
    height: int

class BaseElement(BaseModel):
    id: str
    type: Literal["text", "image", "logo", "packshot", "value_tile"]
    bounds: Rect
    z: int = 0

class TextElement(BaseElement):
    type: Literal["text", "value_tile"]
    text: str
    font_family: str = "Arial"
    font_size: int
    font_weight: Literal["normal", "bold"] = "normal"
    color: RGBA = RGBA(r=0, g=0, b=0, a=1)
    align: Literal["left", "center", "right"] = "center"
    background: Optional[RGBA] = None

class ImageElement(BaseElement):
    type: Literal["image", "logo", "packshot"]
    src: str  # path or URL
    keep_aspect: bool = True

class Canvas(BaseModel):
    format: Format
    width: int
    height: int
    background_color: Optional[RGBA] = RGBA(r=255, g=255, b=255, a=1)
    background_image: Optional[str] = None
    elements: List[BaseElement | TextElement | ImageElement]

class UploadResponse(BaseModel):
    files: List[str]

class LayoutSuggestRequest(BaseModel):
    format: Format
    headline: Optional[str] = None
    subhead: Optional[str] = None
    value_text: Optional[str] = None
    logo: Optional[str] = None
    packshots: List[str] = []

class LayoutSuggestResponse(BaseModel):
    candidates: List[Canvas]

class ComplianceIssue(BaseModel):
    code: str
    message: str
    severity: Literal["error", "warning", "info"] = "error"
    autofix: Optional[dict] = None

class ComplianceRequest(BaseModel):
    canvas: Canvas

class ComplianceResponse(BaseModel):
    passed: bool
    issues: List[ComplianceIssue]

class ExportRequest(BaseModel):
    canvas: Canvas
    output_format: Literal["PNG", "JPG"] = "PNG"

class ExportResponse(BaseModel):
    file_path: str
    url: str
