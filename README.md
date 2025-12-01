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

## Quick Start

### 1) Backend
```powershell
# From repo root (note the en-dash in folder name)
Push-Location "e:\AIRC – AI Retail Creative System\backend"
python -m venv .venv; ".venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2) Frontend
Open a new PowerShell tab:
```powershell
Push-Location "e:\AIRC – AI Retail Creative System\frontend";
npm install; 
npm run dev
```

- Frontend runs at http://localhost:5173
- Backend runs at http://127.0.0.1:8000 (API under `/api`)
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
- Background removal uses a simple near-white remover (PIL). For robust removal, integrate a service like remove.bg.
- OCR for banned copy is not enabled in this prototype; banned terms are checked against user-entered copy.
- Fonts: the renderer tries `Arial`; if not available, it falls back to PIL's default font.

## Roadmap
- Advanced layout generator (Vision + LLM)
- OCR for embedded copy in images
- Server-side auto-fix application
- OCR for images and advanced background removal
- Performance-driven layout suggestions (Vision+LLM)
- User authentication and cloud storage
