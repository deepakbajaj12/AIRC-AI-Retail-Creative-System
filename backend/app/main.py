from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import ASSETS_DIR, EXPORTS_DIR

from .routes.health import router as health_router
from .routes.uploads import router as uploads_router
from .routes.layout import router as layout_router
from .routes.compliance import router as compliance_router
from .routes.export import router as export_router
from .routes.projects import router as projects_router
from .routes.image_tools import router as image_tools_router

app = FastAPI(title="AIRC – AI Retail Creative System", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(uploads_router, prefix="/api")
app.include_router(layout_router, prefix="/api")
app.include_router(compliance_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(image_tools_router, prefix="/api")

app.mount("/static/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
app.mount("/static/exports", StaticFiles(directory=str(EXPORTS_DIR)), name="exports")

@app.get("/")
def root():
    return {"status": "ok", "service": "AIRC API"}
