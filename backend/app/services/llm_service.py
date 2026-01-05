from __future__ import annotations

import os
import json
from typing import Optional, List, Dict, Any

def _enabled() -> bool:
    return os.getenv("AIRC_LLM_ENABLED", "1") not in ("0", "false", "False")


def suggest_compliant_rewrite(text: str) -> Optional[str]:
    """Best-effort Gemini suggestion. Returns None if disabled/unconfigured/fails."""
    if not text or not _enabled():
        return None

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        prompt = (
            "Rewrite this ad copy to be retail-media compliant. "
            "Keep meaning similar, remove/avoid banned claims (e.g., free, win, competition, price claims, sustainability claims), "
            "avoid absolute guarantees, and keep it short. Return ONLY the rewritten copy.\n\n"
            f"COPY: {text}"
        )

        resp = model.generate_content(prompt)
        out = getattr(resp, "text", None)
        if not out:
            return None
        out = out.strip().strip('"').strip("'")
        return out or None
    except Exception:
        return None


def generate_layout_json(
    format_name: str,
    width: int,
    height: int,
    headline: str,
    subhead: str,
    value_text: str,
    logo_url: str,
    packshot_urls: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Asks Gemini to generate a JSON layout for the given elements.
    Returns a dict matching the Canvas schema, or None on failure.
    """
    if not _enabled():
        return None

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        # Construct a description of the elements
        elements_desc = []
        if headline:
            elements_desc.append(f"- Headline text: '{headline}'")
        if subhead:
            elements_desc.append(f"- Subhead text: '{subhead}'")
        if value_text:
            elements_desc.append(f"- Value/Price text: '{value_text}'")
        if logo_url:
            elements_desc.append(f"- Logo image (src='{logo_url}')")
        for i, p in enumerate(packshot_urls):
            elements_desc.append(f"- Packshot image {i+1} (src='{p}')")

        prompt = f"""
        You are an expert graphic designer. Create a JSON layout for a retail banner ad.
        
        Canvas Details:
        - Format: {format_name}
        - Dimensions: {width}x{height} pixels
        
        Elements to Include:
        {chr(10).join(elements_desc)}
        
        Requirements:
        1. Return ONLY valid JSON. No markdown formatting.
        2. The JSON must match this schema structure:
           {{
             "format": "{format_name}",
             "width": {width},
             "height": {height},
             "background_color": {{ "r": 255, "g": 255, "b": 255, "a": 1 }},
             "elements": [
               {{
                 "id": "unique_id",
                 "type": "text" | "image" | "logo" | "packshot" | "value_tile",
                 "text": "string (if text type)",
                 "src": "string (if image type)",
                 "bounds": {{ "x": int, "y": int, "width": int, "height": int }},
                 "font_size": int (if text),
                 "color": {{ "r": int, "g": int, "b": int, "a": 1 }},
                 "background": {{ "r": int, "g": int, "b": int, "a": float }} (optional),
                 "z": int (layer order)
               }}
             ]
           }}
        3. Design Guidelines:
           - **Safe Zones:** Keep all text and logos at least 50px away from any edge. Do NOT place content at y=0 or y={height}.
           - **Style:** Use a clean, modern retail style. Prefer dark text on white background or white text on transparent background if over a clean area. Avoid heavy black bars behind text unless absolutely necessary for contrast.
           - **Logo:** Place the logo in a corner (top-left, top-right) or top-center, with ample padding (at least 40px from top/left).
           - **Packshots:** Center the main product images. Ensure they are large enough but do not touch the edges.
           - **Text:** Ensure headline is prominent. Avoid overlapping text on top of product faces/details.
           - **Value Tile:** Make the price/offer pop (e.g., yellow/red background), but place it strategically (e.g., bottom corner or near product) without covering the product.
        """

        resp = model.generate_content(prompt)
        out = getattr(resp, "text", None)
        if not out:
            return None
        
        # Clean up potential markdown code blocks
        out = out.strip()
        if out.startswith("```json"):
            out = out[7:]
        if out.startswith("```"):
            out = out[3:]
        if out.endswith("```"):
            out = out[:-3]
        
        return json.loads(out.strip())
    except Exception as e:
        print(f"LLM Layout Gen Error: {e}")
        return None


def fallback_rewrite(text: str) -> str:
    """Deterministic fallback if no LLM available."""
    replacements = {
        "free": "great value",
        "win": "discover",
        "competition": "offer",
        "contest": "offer",
        "guarantee": "designed to",
        "clinically proven": "tested",
        "sustainable": "responsible",
        "eco": "responsible",
        "environment": "responsible",
    }
    out = text
    low = out.lower()
    for k, v in replacements.items():
        if k in low:
            # simple case-insensitive replace
            out = _ci_replace(out, k, v)
            low = out.lower()

    # remove currency symbols and obvious price patterns (demo-safe)
    out = out.replace("£", "")
    return " ".join(out.split()).strip()


def _ci_replace(s: str, old: str, new: str) -> str:
    import re

    return re.sub(re.escape(old), new, s, flags=re.IGNORECASE)
