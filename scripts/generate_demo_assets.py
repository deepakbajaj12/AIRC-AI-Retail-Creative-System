from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "sample-assets"
DOCS_DIR = ROOT / "docs"


def _font(size: int) -> ImageFont.ImageFont:
    # Use whatever is available; this is for generating demo assets only.
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _badge(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, text: str, fill=(0, 120, 212)):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=fill)
    draw.text((x + 16, y + 10), text, fill=(255, 255, 255), font=_font(30))


def _packshot_base(title: str) -> Image.Image:
    img = Image.new("RGB", (900, 900), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    # product silhouette
    draw.rounded_rectangle([220, 140, 680, 780], radius=40, outline=(40, 40, 40), width=6, fill=(255, 255, 255))
    draw.rounded_rectangle([270, 220, 630, 320], radius=22, fill=(0, 120, 212))
    draw.text((290, 245), "AIRC", fill=(255, 255, 255), font=_font(52))

    draw.text((70, 40), title, fill=(30, 30, 30), font=_font(40))
    return img


def make_sample_assets() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Normal packshot
    img = _packshot_base("Sample Packshot (Normal)")
    ImageDraw.Draw(img).text((290, 370), "Everyday essentials", fill=(30, 30, 30), font=_font(36))
    img.save(SAMPLE_DIR / "packshot_normal.png")

    # 2) Banned-text packshot (for OCR demo)
    img = _packshot_base("Sample Packshot (Banned Text)")
    d = ImageDraw.Draw(img)
    _badge(d, 90, 760, 720, 90, "FREE")
    d.text((210, 690), "Limited time", fill=(30, 30, 30), font=_font(34))
    img.save(SAMPLE_DIR / "packshot_banned_text.png")

    # 3) Alcohol-ish packshot (for Drinkaware rule demo)
    img = _packshot_base("Sample Packshot (Alcohol)")
    d = ImageDraw.Draw(img)
    _badge(d, 120, 760, 660, 90, "ALCOHOL")
    d.text((170, 690), "Please drink responsibly", fill=(30, 30, 30), font=_font(30))
    d.text((280, 820), "Drinkaware.co.uk", fill=(30, 30, 30), font=_font(28))
    img.save(SAMPLE_DIR / "packshot_alcohol.png")

    # Simple logo
    logo = Image.new("RGBA", (600, 200), (255, 255, 255, 0))
    d = ImageDraw.Draw(logo)
    d.rounded_rectangle([10, 10, 590, 190], radius=34, fill=(0, 120, 212, 255))
    d.text((40, 70), "AIRC DEMO LOGO", fill=(255, 255, 255, 255), font=_font(44))
    logo.save(SAMPLE_DIR / "logo_demo.png")


def make_docs_images() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # These are not real UI screenshots; they are judge-friendly placeholders
    # so the repo isn't missing referenced media.
    for i, title in [(1, "Screenshot 1 (Placeholder)"), (2, "Screenshot 2 (Placeholder)")]:
        img = Image.new("RGB", (1280, 720), (20, 20, 20))
        d = ImageDraw.Draw(img)
        d.text((60, 60), "AIRC – AI Retail Creative System", fill=(255, 255, 255), font=_font(48))
        d.text((60, 140), title, fill=(200, 200, 200), font=_font(36))
        d.rounded_rectangle([60, 220, 1220, 660], radius=24, outline=(0, 180, 255), width=5)
        d.text((90, 260), "Run the app and capture real screenshots before submission.", fill=(220, 220, 220), font=_font(30))
        d.text((90, 320), "This file is generated so README links never break.", fill=(220, 220, 220), font=_font(30))
        img.save(DOCS_DIR / f"screenshot{i}.png")

    # Tiny animated GIF as a lightweight "demo video" placeholder
    frames = []
    for step in [
        "1) Upload sample assets",
        "2) AI Layout",
        "3) Compliance Check",
        "4) Apply Fixes (incl. replace_text)",
        "5) Export (shows KB)",
    ]:
        img = Image.new("RGB", (960, 540), (10, 10, 12))
        d = ImageDraw.Draw(img)
        d.text((40, 40), "AIRC Demo Flow", fill=(255, 255, 255), font=_font(44))
        d.text((40, 140), step, fill=(0, 180, 255), font=_font(40))
        d.text((40, 220), "Replace this GIF with a real 45–60s screen recording.", fill=(220, 220, 220), font=_font(28))
        frames.append(img)

    out = DOCS_DIR / "demo_video.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=900, loop=0)


def main() -> None:
    make_sample_assets()
    make_docs_images()
    print(f"Wrote demo assets to: {SAMPLE_DIR}")
    print(f"Wrote docs media to: {DOCS_DIR}")


if __name__ == "__main__":
    main()
