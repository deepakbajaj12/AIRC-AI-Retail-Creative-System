from __future__ import annotations

import os
from typing import Optional


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
