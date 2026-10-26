import os
import logging
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

try:
    from supabase import create_client
except ImportError:
    create_client = None
    logger.warning("supabase-py is not installed; using local file storage")

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "documents")


supabase: Any | None = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    if create_client is None:
        logger.warning(
            "Supabase credentials are set but supabase-py is unavailable; "
            "using local file storage"
        )
    else:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
elif SUPABASE_URL or SUPABASE_SERVICE_KEY:
    logger.warning(
        "Supabase storage is not configured: set both SUPABASE_URL and "
        "SUPABASE_SERVICE_KEY"
    )
else:
    logger.info("Supabase storage credentials are not configured; using local file storage")


UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def upload_file(
    file_content: bytes,
    storage_path: str,
    content_type: str,
):
    # Always save a local copy as reliable fallback
    try:
        local_target = UPLOAD_DIR / storage_path
        local_target.parent.mkdir(parents=True, exist_ok=True)
        local_target.write_bytes(file_content)
    except Exception as e:
        print("Warning: failed to save local copy:", str(e))

    # Attempt upload to Supabase if client is available
    if supabase is not None:
        try:
            supabase.storage.from_(SUPABASE_BUCKET).upload(
                path=storage_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "upsert": "true",
                },
            )
            return {"path": storage_path, "provider": "supabase"}
        except Exception as e:
            print(f"Warning: Supabase upload error ({str(e)}). Using local file fallback.")
    # Fallback when supabase unavailable or upload failed
    return {"path": storage_path, "provider": "local"}


def delete_file(storage_path: str):
    # Remove local file if exists
    try:
        local_target = UPLOAD_DIR / storage_path
        if local_target.exists():
            local_target.unlink()
    except Exception as e:
        print("Warning: failed to delete local file:", str(e))

    # Attempt Supabase delete if client available
    if supabase is not None:
        try:
            return (
                supabase.storage
                .from_(SUPABASE_BUCKET)
                .remove([
                    storage_path
                ])
            )
        except Exception as e:
            print("Warning: failed to delete file from Supabase storage:", str(e))
    # Fallback when supabase unavailable
    return None


def create_file_url(
    storage_path: str,
    expires_in: int = 3600,
):
    if supabase is not None:
        try:
            res = (
                supabase.storage
                .from_(SUPABASE_BUCKET)
                .create_signed_url(
                    storage_path,
                    expires_in,
                )
            )
            if isinstance(res, dict):
                url = res.get("signedURL") or res.get("signedUrl")
                if url:
                    return url
            if res and not str(res).startswith("{"):
                return str(res)
        except Exception:
            logger.exception("Could not create a signed Supabase file URL")

        try:
            pub = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
            if pub:
                return pub
        except Exception:
            logger.exception("Could not create a public Supabase file URL")

    local_target = UPLOAD_DIR / storage_path
    if local_target.exists():
        backend_base = os.getenv(
            "BACKEND_URL",
            os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000"),
        ).rstrip("/")
        return f"{backend_base}/uploads/{storage_path}"

    return None
