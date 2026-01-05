from __future__ import annotations

from typing import List
from ..models.schemas import Canvas, TextElement, ImageElement, BaseElement, Rect, RGBA, Format
from ..config import FORMATS, SAFE_ZONES
from .llm_service import generate_layout_json

# Z-index constants
Z_BG = 0
Z_IMAGE = 10
Z_TEXT_BG = 15
Z_HEADLINE = 20
Z_SUBHEAD = 21
Z_VALUE = 30
Z_LOGO = 40

def _get_safe_zones(format: Format):
    w, h = FORMATS[format]
    t, r, b, l = SAFE_ZONES.get(format, (150, 150, 150, 150))
    # Force minimum margins to prevent edge-hugging
    return w, h, max(t, 50), max(r, 50), max(b, 50), max(l, 50)

def _calc_text_height(text: str, font_size: int, width: int) -> int:
    # Rough estimation of text height
    if not text: return 0
    chars_per_line = max(1, width // (font_size // 2))
    lines = (len(text) // chars_per_line) + 1
    return int(lines * font_size * 1.3)

def _arrange_packshots(packshots: List[str], bounds: Rect, z_start: int) -> List[ImageElement]:
    elements = []
    count = min(len(packshots), 3)
    if count == 0:
        return elements
    
    # Simple horizontal arrangement
    padding = 20
    # Calculate width for each item
    item_w = (bounds.width - (padding * (count - 1))) // count
    
    for i in range(count):
        x = bounds.x + i * (item_w + padding)
        y = bounds.y
        elements.append(ImageElement(
            id=f"packshot_{i}",
            type="packshot",
            src=packshots[i],
            bounds=Rect(x=x, y=y, width=item_w, height=bounds.height),
            z=z_start + i
        ))
    return elements

def _generate_landscape_standard(format, headline, subhead, value_text, logo, packshots) -> Canvas:
    """Standard Landscape: Image Left, Text Right"""
    w, h, t, r, b, l = _get_safe_zones(format)
    elements: List[BaseElement] = []
    mid_x = w // 2
    
    # 1. Logo (Top Right)
    if logo:
        elements.append(ImageElement(
            id="logo", type="logo", src=logo, 
            bounds=Rect(x=w - r - 150, y=t, width=150, height=90), z=Z_LOGO
        ))

    # 2. Packshots (Left Half)
    if packshots:
        avail_w = mid_x - l - 20
        avail_h = h - t - b
        
        # Adjust width based on count to avoid tiny images if we have 3
        # But we are constrained by half width.
        ps_rect = Rect(x=l, y=t, width=avail_w, height=avail_h)
        
        # Center the group vertically/horizontally if possible?
        # For now, just fill the area with _arrange_packshots logic
        # We might want to center the *group* of packshots.
        
        # Let's define a max width for the group
        group_w = min(avail_w, 600)
        group_h = min(avail_h, 500)
        
        # Center the group rect
        group_x = l + (avail_w - group_w) // 2
        group_y = t + (avail_h - group_h) // 2
        
        elements.extend(_arrange_packshots(packshots, Rect(x=group_x, y=group_y, width=group_w, height=group_h), Z_IMAGE))

    # 3. Text (Right Half)
    txt_x = mid_x + 40
    txt_w = w - r - txt_x
    
    # Text BG
    elements.append(TextElement(
        id="text_bg", type="text", text=" ", font_size=1, 
        bounds=Rect(x=mid_x, y=0, width=w-mid_x, height=h), z=Z_TEXT_BG, 
        background=RGBA(r=255, g=255, b=255, a=1.0)
    ))

    current_y = t + 80
    if headline:
        hl_size = 48
        hl_h = _calc_text_height(headline, hl_size, txt_w)
        elements.append(TextElement(
            id="headline", type="text", text=headline, font_family="Arial", font_size=hl_size,
            font_weight="bold", color=RGBA(r=0, g=0, b=0, a=1), align="left", 
            bounds=Rect(x=txt_x, y=current_y, width=txt_w, height=hl_h), z=Z_HEADLINE
        ))
        current_y += hl_h + 20
    
    if subhead:
        sh_size = 32
        sh_h = _calc_text_height(subhead, sh_size, txt_w)
        elements.append(TextElement(
            id="subhead", type="text", text=subhead, font_family="Arial", font_size=sh_size,
            font_weight="normal", color=RGBA(r=0, g=0, b=0, a=1), align="left", 
            bounds=Rect(x=txt_x, y=current_y, width=txt_w, height=sh_h), z=Z_SUBHEAD
        ))
        current_y += sh_h + 20

    if value_text:
        elements.append(TextElement(
            id="value", type="value_tile", text=value_text, font_family="Arial", font_size=48,
            font_weight="bold", color=RGBA(r=255, g=255, b=0, a=1), background=RGBA(r=0, g=0, b=0, a=1),
            align="center", bounds=Rect(x=txt_x, y=current_y, width=min(300, txt_w), height=100), z=Z_VALUE
        ))

    return Canvas(format=format, width=w, height=h, background_color=RGBA(r=255, g=255, b=255, a=1), elements=elements)

def _generate_landscape_inverted(format, headline, subhead, value_text, logo, packshots) -> Canvas:
    """Inverted Landscape: Text Left, Image Right"""
    w, h, t, r, b, l = _get_safe_zones(format)
    elements: List[BaseElement] = []
    mid_x = w // 2
    
    # 1. Logo (Top Left)
    if logo:
        elements.append(ImageElement(
            id="logo", type="logo", src=logo, 
            bounds=Rect(x=l, y=t, width=150, height=90), z=Z_LOGO
        ))

    # 2. Packshots (Right Half)
    if packshots:
        avail_w = (w - r) - mid_x - 20
        avail_h = h - t - b
        
        group_w = min(avail_w, 600)
        group_h = min(avail_h, 500)
        
        group_x = mid_x + 20 + (avail_w - group_w) // 2
        group_y = t + (avail_h - group_h) // 2
        
        elements.extend(_arrange_packshots(packshots, Rect(x=group_x, y=group_y, width=group_w, height=group_h), Z_IMAGE))

    # 3. Text (Left Half)
    txt_x = l
    txt_w = mid_x - l - 40
    
    # Text BG
    elements.append(TextElement(
        id="text_bg", type="text", text=" ", font_size=1, 
        bounds=Rect(x=0, y=0, width=mid_x, height=h), z=Z_TEXT_BG, 
        background=RGBA(r=255, g=255, b=255, a=1.0)
    ))

    current_y = t + 120
    if headline:
        hl_size = 48
        hl_h = _calc_text_height(headline, hl_size, txt_w)
        elements.append(TextElement(
            id="headline", type="text", text=headline, font_family="Arial", font_size=hl_size,
            font_weight="bold", color=RGBA(r=0, g=0, b=0, a=1), align="left", 
            bounds=Rect(x=txt_x, y=current_y, width=txt_w, height=hl_h), z=Z_HEADLINE
        ))
        current_y += hl_h + 20
    
    if subhead:
        sh_size = 32
        sh_h = _calc_text_height(subhead, sh_size, txt_w)
        elements.append(TextElement(
            id="subhead", type="text", text=subhead, font_family="Arial", font_size=sh_size,
            font_weight="normal", color=RGBA(r=0, g=0, b=0, a=1), align="left", 
            bounds=Rect(x=txt_x, y=current_y, width=txt_w, height=sh_h), z=Z_SUBHEAD
        ))
        current_y += sh_h + 20

    if value_text:
        elements.append(TextElement(
            id="value", type="value_tile", text=value_text, font_family="Arial", font_size=48,
            font_weight="bold", color=RGBA(r=255, g=255, b=0, a=1), background=RGBA(r=0, g=0, b=0, a=1),
            align="center", bounds=Rect(x=txt_x, y=current_y, width=min(300, txt_w), height=100), z=Z_VALUE
        ))

    return Canvas(format=format, width=w, height=h, background_color=RGBA(r=255, g=255, b=255, a=1), elements=elements)

def _generate_vertical_standard(format, headline, subhead, value_text, logo, packshots) -> Canvas:
    """Standard Vertical: Logo Top Left, Text Top, Packshot Bottom Right, Value Bottom Left"""
    w, h, t, r, b, l = _get_safe_zones(format)
    elements: List[BaseElement] = []
    safe_w = w - l - r
    
    current_y = t + 20
    
    # 1. Logo (Top Left)
    if logo:
        elements.append(ImageElement(
            id="logo", type="logo", src=logo, 
            bounds=Rect(x=l, y=current_y, width=200, height=120), z=Z_LOGO
        ))
        current_y += 140

    # 2. Text (Top/Center)
    if headline:
        hl_size = 56
        hl_h = _calc_text_height(headline, hl_size, safe_w)
        elements.append(TextElement(
            id="headline", type="text", text=headline, font_family="Arial", font_size=hl_size,
            font_weight="bold", color=RGBA(r=0, g=0, b=0, a=1), align="center", 
            bounds=Rect(x=l, y=current_y, width=safe_w, height=hl_h), z=Z_HEADLINE
        ))
        current_y += hl_h + 20

    if subhead:
        sh_size = 32
        sh_h = _calc_text_height(subhead, sh_size, safe_w)
        elements.append(TextElement(
            id="subhead", type="text", text=subhead, font_family="Arial", font_size=sh_size,
            font_weight="normal", color=RGBA(r=0, g=0, b=0, a=1), align="center", 
            bounds=Rect(x=l, y=current_y, width=safe_w, height=sh_h), z=Z_SUBHEAD
        ))

    # 3. Bottom Area
    bottom_area_h = 500
    
    # Packshot (Bottom Right)
    if packshots:
        # If multiple packshots, we might need more width.
        # Standard vertical usually puts packshot in bottom right.
        # If 3 packshots, maybe use full width?
        
        if len(packshots) > 1:
             # Use full width for multiple packshots at bottom
            ps_w = min(safe_w, 700)
            ps_h = min(bottom_area_h, 500)
            ps_x = l + (safe_w - ps_w) // 2
            ps_y = h - b - ps_h
            elements.extend(_arrange_packshots(packshots, Rect(x=ps_x, y=ps_y, width=ps_w, height=ps_h), Z_IMAGE))
        else:
            # Single packshot - keep original "Hero" placement
            ps_w = min(safe_w // 2 + 100, 600)
            ps_h = min(bottom_area_h, 600)
            ps_x = w - r - ps_w
            ps_y = h - b - ps_h
            elements.append(ImageElement(
                id="packshot_0", type="packshot", src=packshots[0], 
                bounds=Rect(x=ps_x, y=ps_y, width=ps_w, height=ps_h), z=Z_IMAGE
            ))

    # Value Tile (Bottom Left)
    if value_text:
        val_w = 320
        val_h = 140
        val_x = l
        # If multiple packshots used full width, we need to overlay value or move it up
        if packshots and len(packshots) > 1:
             val_y = h - b - val_h - 20 - 100 # Move up a bit? Or overlay?
             # Let's overlay on bottom left
             val_y = h - b - val_h - 20
        else:
             val_y = h - b - val_h - 20
             
        elements.append(TextElement(
            id="value", type="value_tile", text=value_text, font_family="Arial", font_size=56,
            font_weight="bold", color=RGBA(r=255, g=255, b=0, a=1), background=RGBA(r=0, g=0, b=0, a=1),
            align="center", bounds=Rect(x=val_x, y=val_y, width=val_w, height=val_h), z=Z_VALUE
        ))

    return Canvas(format=format, width=w, height=h, background_color=RGBA(r=255, g=255, b=255, a=1), elements=elements)

def _generate_vertical_centered(format, headline, subhead, value_text, logo, packshots) -> Canvas:
    """Centered Vertical: Logo Top Center, Text Center, Packshot Bottom Center"""
    w, h, t, r, b, l = _get_safe_zones(format)
    elements: List[BaseElement] = []
    safe_w = w - l - r
    
    current_y = t + 20
    
    # 1. Logo (Top Center)
    if logo:
        logo_w = 200
        logo_x = l + (safe_w - logo_w) // 2
        elements.append(ImageElement(
            id="logo", type="logo", src=logo, 
            bounds=Rect(x=logo_x, y=current_y, width=logo_w, height=120), z=Z_LOGO
        ))
        current_y += 140

    # 2. Text (Center)
    if headline:
        hl_size = 56
        hl_h = _calc_text_height(headline, hl_size, safe_w)
        elements.append(TextElement(
            id="headline", type="text", text=headline, font_family="Arial", font_size=hl_size,
            font_weight="bold", color=RGBA(r=0, g=0, b=0, a=1), align="center", 
            bounds=Rect(x=l, y=current_y, width=safe_w, height=hl_h), z=Z_HEADLINE
        ))
        current_y += hl_h + 20

    if subhead:
        sh_size = 32
        sh_h = _calc_text_height(subhead, sh_size, safe_w)
        elements.append(TextElement(
            id="subhead", type="text", text=subhead, font_family="Arial", font_size=sh_size,
            font_weight="normal", color=RGBA(r=0, g=0, b=0, a=1), align="center", 
            bounds=Rect(x=l, y=current_y, width=safe_w, height=sh_h), z=Z_SUBHEAD
        ))

    # 3. Packshot (Bottom Center)
    if packshots:
        ps_w = min(safe_w, 600)
        ps_h = min(500, 600)
        ps_x = l + (safe_w - ps_w) // 2
        ps_y = h - b - ps_h - 20
        
        elements.extend(_arrange_packshots(packshots, Rect(x=ps_x, y=ps_y, width=ps_w, height=ps_h), Z_IMAGE))
        
        # Value Tile (Overlaid on Packshot or just above it)
        if value_text:
            val_w = 300
            val_h = 100
            val_x = ps_x + ps_w - val_w + 20 # Offset to right
            val_y = ps_y - 50 # Overlap top right corner
            elements.append(TextElement(
                id="value", type="value_tile", text=value_text, font_family="Arial", font_size=48,
                font_weight="bold", color=RGBA(r=255, g=255, b=0, a=1), background=RGBA(r=0, g=0, b=0, a=1),
                align="center", bounds=Rect(x=val_x, y=val_y, width=val_w, height=val_h), z=Z_VALUE
            ))
    elif value_text:
         # Just value at bottom if no packshot
        val_w = 320
        val_h = 140
        val_x = l + (safe_w - val_w) // 2
        val_y = h - b - val_h - 20
        elements.append(TextElement(
            id="value", type="value_tile", text=value_text, font_family="Arial", font_size=56,
            font_weight="bold", color=RGBA(r=255, g=255, b=0, a=1), background=RGBA(r=0, g=0, b=0, a=1),
            align="center", bounds=Rect(x=val_x, y=val_y, width=val_w, height=val_h), z=Z_VALUE
        ))

    return Canvas(format=format, width=w, height=h, background_color=RGBA(r=255, g=255, b=255, a=1), elements=elements)


def suggest_layouts(
    format: Format,
    headline: str | None,
    subhead: str | None,
    value_text: str | None,
    logo: str | None,
    packshots: list[str],
) -> List[Canvas]:
    
    candidates = []
    
    # 1. Try LLM Generation
    w, h = FORMATS[format]
    llm_data = generate_layout_json(
        format, w, h, headline, subhead, value_text, logo, packshots
    )
    if llm_data:
        try:
            # Ensure format is correct enum
            llm_data["format"] = format
            candidates.append(Canvas(**llm_data))
        except Exception as e:
            print(f"Error parsing LLM layout: {e}")

    # 2. Algorithmic Fallbacks
    if format == "LANDSCAPE":
        candidates.append(_generate_landscape_standard(format, headline, subhead, value_text, logo, packshots))
        candidates.append(_generate_landscape_inverted(format, headline, subhead, value_text, logo, packshots))
    else:
        candidates.append(_generate_vertical_standard(format, headline, subhead, value_text, logo, packshots))
        candidates.append(_generate_vertical_centered(format, headline, subhead, value_text, logo, packshots))
        
    return candidates
