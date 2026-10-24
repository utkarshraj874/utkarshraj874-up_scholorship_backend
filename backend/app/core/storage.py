import os
from pathlib import Path
from dotenv import load_dotenv
try:
    from supabase import create_client, Client
except ImportError:
    # Supabase client is optional; define dummy types
    create_client = None
    Client = None
    print("Warning: supabase-py not installed. Storage will use only local fallback.")

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "documents")


if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL is not configured")
    if not SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_SERVICE_KEY is not configured")
    supabase: Client = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_KEY
    )
else:
    supabase = None


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
            return (
                supabase.storage
                .from_(SUPABASE_BUCKET)
                .upload(
                    path=storage_path,
                    file=file_content,
                    file_options={
                        "content-type": content_type,
                        "upsert": "true",
                    },
                )
            )
        except Exception as e:
            print(f"Warning: Supabase upload error ({str(e)}). Using local file fallback.")
    # Fallback when supabase unavailable or upload failed
    return {"path": storage_path, "local": True}


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
    except Exception as e:
        print("Supabase signed URL error:", str(e))

    # Fallback to public URL or local mounted static URL
    try:
        pub = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
        if pub:
            return pub
    except Exception:
        pass

    # If local file exists, serve from local API endpoint
    local_target = UPLOAD_DIR / storage_path
    if local_target.exists():
        return f"http://localhost:8000/uploads/{storage_path}"

    return None
