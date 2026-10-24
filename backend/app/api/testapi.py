from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.core.storage import (
    supabase,
    SUPABASE_BUCKET
)

import traceback


router = APIRouter(
    prefix="/storage",
    tags=["Storage"]
)


@router.post("/test-upload")
async def test_upload(
    file: UploadFile = File(...)
):

    try:
        print("\n==============================")
        print("UPLOAD STARTED")
        print("==============================")

        # 1. File information
        print("File name:", file.filename)
        print("Content type:", file.content_type)

        # 2. Check bucket
        print("Bucket:", SUPABASE_BUCKET)

        if not SUPABASE_BUCKET:
            raise Exception("SUPABASE_BUCKET is empty!")

        # 3. Read file
        file_content = await file.read()

        print("File size:", len(file_content), "bytes")

        if not file_content:
            raise Exception("Uploaded file is empty!")

        # 4. Create storage path
        storage_path = f"test/{file.filename}"

        print("Storage path:", storage_path)

        # 5. Upload to Supabase
        print("Uploading to Supabase...")

        response = (
            supabase.storage
            .from_(SUPABASE_BUCKET)
            .upload(
                path=storage_path,
                file=file_content,
                file_options={
                    "content-type": file.content_type or "application/octet-stream",
                    "upsert": "false"
                }
            )
        )

        print("SUPABASE RESPONSE:")
        print(response)

        print("==============================")
        print("UPLOAD SUCCESS")
        print("==============================")

        return {
            "message": "File uploaded successfully",
            "path": storage_path,
            "file_name": file.filename,
            "file_type": file.content_type,
            "file_size": len(file_content),
            "supabase_response": str(response)
        }

    except Exception as e:

        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("UPLOAD ERROR")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        print("Error type:", type(e).__name__)
        print("Error message:", str(e))

        print("\nFULL TRACEBACK:")
        traceback.print_exc()

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

        raise HTTPException(
            status_code=500,
            detail={
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )