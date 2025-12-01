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
- OCR: enabled via `pytesseract` to detect banned text inside images. Install Tesseract:
	- Windows: https://github.com/UB-Mannheim/tesseract/wiki
	- macOS: `brew install tesseract`
	- Linux: `sudo apt-get install tesseract-ocr`
- Fonts: the renderer tries `Arial`. To avoid mismatches, consider bundling a TTF under `backend/fonts/` and adjust renderer.

## Demo (60s)
Upload the 3 sample images in `/sample-assets` (normal, banned-text, alcohol), click AI Layout → Compliance Check → Apply Fixes → Export PNG. If OCR is set up, the banned-text packshot will be flagged.

## Roadmap
- Advanced layout generator (Vision + LLM)
- Rich auto-fix application on the client and server
- Server-side OCR visual highlights
- User authentication and cloud storage

## Media
- Demo video: `docs/demo_video.mp4`
- Screenshots: `docs/screenshot1.png`, `docs/screenshot2.png`
 
## Assets
- Sample assets: add 3 images under `sample-assets/` and upload them via the UI.
- Bundled font: place a TTF under `backend/fonts/` (e.g., `Inter-Regular.ttf`) to ensure consistent rendering.

## Exports
- Exports are under `backend/exports/` and served at `/static/exports`. JPG exports are compressed under 500KB via an iterative quality loop.
- Judges: verify an example export file size is < 500KB.
