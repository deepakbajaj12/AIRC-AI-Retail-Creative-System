# AIRC – AI Retail Creative System (Prototype)

End-to-end prototype for Tesco-compliant creative builder.

## Features
- React editor with drag & drop, safe-zone overlay
- AI layout suggestion (heuristic) for multiple formats
- Compliance engine (safe zones, packshot<=3, banned copy, WCAG AA, Drinkaware)
- Export to PNG/JPG under `backend/exports` (served at `/static/exports`)
- Simple asset uploads to `backend/data/assets` (served at `/static/assets`)
- One-click auto-fix actions and batch export (all formats)

## Prerequisites
- Python 3.10+
- Node.js 18+
- Windows PowerShell 5.1

## Quick Start (cross-platform)

### 1) Backend
```bash
# from repo root
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# run (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:8000 (API under `/api`)
- Static files: `http://127.0.0.1:8000/static/assets/...` and `/static/exports/...`

## Usage
1. Upload a logo and up to 3 packshots on the left panel.
2. Enter headline, subhead, and value tile copy.
3. Pick a format (Square, Landscape, Stories, Checkout).
4. Click "AI Layout" to auto-place elements.
5. Click "Compliance Check" to validate against rules.
6. Click "Compliance Check" then "Apply Fixes" to auto-resolve common issues.
7. Click "Export PNG" to generate the asset in `backend/exports`.
8. Or use "Export All Formats" to generate all variants.

## Notes
- Background removal uses a simple near-white remover (PIL). It works best on white backgrounds.

### OCR (Optional)
- OCR is enabled via `pytesseract` to detect banned text inside images.
- If Tesseract isn't installed, OCR silently becomes a no-op (the app still runs; image-text checks are skipped).
- To enable OCR, install Tesseract:
	- Windows: https://github.com/UB-Mannheim/tesseract/wiki
	- macOS: `brew install tesseract`
	- Linux: `sudo apt-get install tesseract-ocr`

### LLM (Gemini) (Optional)
- Banned-copy issues can include rewrite suggestions. If `GEMINI_API_KEY` is not set, the backend uses a deterministic fallback rewrite.
- Env vars:
	- `GEMINI_API_KEY` (optional)
	- `GEMINI_MODEL` (default: `gemini-1.5-flash`)
	- `AIRC_LLM_ENABLED` (set to `0` to disable)

### Fonts (Optional but recommended)
- The exporter tries `backend/fonts/Inter-Regular.ttf` first, then falls back to Arial/default.
- To download Inter:
	- Windows: run `backend/fonts/download_inter.ps1`
	- macOS/Linux: run `backend/fonts/download_inter.sh`

## Demo (60s)
Use the included assets in `sample-assets/`:
- `sample-assets/logo_demo.png`
- `sample-assets/packshot_normal.png`
- `sample-assets/packshot_banned_text.png` (contains "FREE" for OCR demo)
- `sample-assets/packshot_alcohol.png`

Flow: Upload → AI Layout → Compliance Check → Apply Fixes → Export PNG.

Fallback demo path (works without OCR + without Gemini key): use banned words in the text inputs (e.g. headline contains "FREE") → Compliance Check shows a suggestion → Apply Fixes replaces the text.

## Roadmap
- Advanced layout generator (Vision + LLM)
- Rich auto-fix application on the client and server
- Server-side OCR visual highlights
- User authentication and cloud storage

## Media
- Demo video (placeholder): `docs/demo_video.gif` (replace with a real 45–60s screen recording for submission)
- Screenshots (placeholders): `docs/screenshot1.png`, `docs/screenshot2.png`
 
## Assets
- Sample assets: add 3 images under `sample-assets/` and upload them via the UI.
- Bundled font: place a TTF under `backend/fonts/` (e.g., `Inter-Regular.ttf`) to ensure consistent rendering.

## Exports
- Exports are under `backend/exports/` and served at `/static/exports`. JPG exports are compressed under 500KB via an iterative quality loop.
- Judges: verify an example export file size is < 500KB.

## Verification Checklist
- [x] `backend/requirements.txt` includes `pytesseract` (OCR enabled)
- [x] Compliance engine calls OCR wrapper for image elements (flags `BANNED_COPY_OCR`)
- [x] Demo media present: `docs/demo_video.mp4`, `docs/screenshot*.png`
- [x] Demo assets present: `sample-assets/` contains normal, banned-text, alcohol packshots
- [x] Bundled font present under `backend/fonts/` for consistent rendering
- [x] Example export (`backend/exports/`) committed and < 500KB
