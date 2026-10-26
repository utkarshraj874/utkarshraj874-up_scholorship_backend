import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure project root is in sys.path so 'backend.app' works from any working directory
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.app.api.user import router as user_router
from backend.app.api.profile import router as profile_router
from backend.app.api.documents import router as documents_router
from backend.app.api.admin import router as admin_router
from backend.app.api.notifications import router as notifications_router
from backend.app.api.help_desk import router as help_desk_router
from backend.app.api.password_reset import router as password_reset_router
from backend.app.api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup if database is configured
    try:
        from backend.app.models import Base
        from backend.app.core.database import engine
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Warning: database table initialization error on startup: {e}")
    yield


app = FastAPI(
    title="UP Scholarship Portal - IIIT Ranchi",
    description="Backend API for UP Scholarship (IIIT Ranchi)",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local React development, Vercel frontend, and external access
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
extra_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://upscholorshipfrontend.vercel.app",
]

all_allowed_origins = list(dict.fromkeys(default_origins + extra_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_allowed_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^https://.*\.vercel\.app$",
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
app.include_router(password_reset_router)
app.include_router(chat_router)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    origin = request.headers.get("origin")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Allow-Headers"] = "*"
        headers["Access-Control-Allow-Methods"] = "*"
    return JSONResponse(
        status_code=500,
        content={"detail": f"Database / Server error: {str(exc)}"},
        headers=headers,
    )


@app.get("/health")
def health_check():
    info = {"status": "ok", "portal": "UP Scholarship Copilot - IIIT Ranchi"}
    try:
        from backend.app.core.config import DATABASE_URL
        from backend.app.core.database import engine
        from sqlalchemy import text, inspect
        import re

        if not DATABASE_URL:
            info["database_status"] = "DATABASE_URL is not set in environment"
        else:
            masked = re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", DATABASE_URL)
            info["database_url"] = masked

            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                info["database_status"] = "connected"
                inspector = inspect(engine)
                info["tables"] = inspector.get_table_names()
    except Exception as e:
        info["database_status"] = "error"
        info["database_error"] = str(e)
    return info




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
