import sys
from pathlib import Path

# Ensure project root is in sys.path so 'backend.app' works from any working directory
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.api.user import router as user_router
from backend.app.api.profile import router as profile_router
from backend.app.api.documents import router as documents_router
from backend.app.api.admin import router as admin_router
from backend.app.api.notifications import router as notifications_router
from backend.app.api.help_desk import router as help_desk_router

app = FastAPI(
    title="UP Scholarship Portal - IIIT Ranchi",
    description="Backend API for UP Scholarship (IIIT Ranchi)",
    version="1.0.0"
)

# Enable CORS for local React development and external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(user_router)
app.include_router(profile_router)
app.include_router(documents_router)
app.include_router(admin_router)
app.include_router(notifications_router)
app.include_router(help_desk_router)



# Mount uploads directory for document previews
uploads_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Serve frontend build if exists
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if not frontend_dist.exists():
    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    if (frontend_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")


    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't hijack docs or openapi
        if full_path in ["docs", "redoc", "openapi.json"]:
            return None
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "message": "UP Scholarship Backend API is running",
            "portal": "UP Scholarship Copilot - IIIT Ranchi",
            "docs": "/docs"
        }
