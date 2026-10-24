import uuid
#used to generate unique id 
from pathlib import Path
#helps work with file name and extension 

from fastapi import UploadFile
#represents an uploaded file in FastAPI
from sqlalchemy.orm import Session

from backend.app.models.documents import Document
from backend.app.core.storage import (
    upload_file,
    delete_file,
    create_file_url,
)
from backend.app.utils.documents_validation import (
    validate_document_details,
)


MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_FILE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


def create_storage_path(
    user_id: int,
    category: str,
    filename: str,
):
    extension = Path(filename).suffix.lower()
    #extracts the file extension(.pdf,.jpg,etc) from the original filename and converts it to lowercase

    unique_name = f"{uuid.uuid4()}{extension}"
    #create a random unique filename using uuid4 and append the original file extension to it
    #eg:-7fea23aede.pdf
    return f"users/{user_id}/{category}/{unique_name}"
    #users/1/pan/7f9a23de.pdf

async def create_document(
    db: Session,
    user_id: int,
    category: str,
    details: dict,
    file: UploadFile,
):
    # Validate document details
    validate_document_details(
        category,
        details,
    )

    # Validate file type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise ValueError(
            "Only PDF, JPG and PNG files are allowed"
        )

    # Read file
    file_content = await file.read()

    # Validate file size
    if not file_content:
        raise ValueError("Uploaded file is empty")

    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(
            "File size must be less than 5 MB"
        )

    # Check existing document
    existing_document = (
        db.query(Document)
        .filter(
            Document.user_id == user_id,
            Document.category == category,
        )
        .first()
    )

    if existing_document:
        await file.seek(0)
        return await update_document(
            db=db,
            user_id=user_id,
            category=category,
            details=details,
            file=file,
        )

    # Create storage path
    storage_path = create_storage_path(
        user_id,
        category,
        file.filename,
    )

    # Upload to Supabase
    upload_file(
        file_content=file_content,
        storage_path=storage_path,
        content_type=file.content_type,
    )

    try:
        document = Document(
            user_id=user_id,
            category=category,
            file_name=file.filename,
            file_type=file.content_type,
            file_size=len(file_content),
            file_path=storage_path,
            storage_provider="supabase",
            **details,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()

        # Remove uploaded file if DB save fails
        delete_file(storage_path)

        raise


def get_user_documents(
    db: Session,
    user_id: int,
):
    return (
        db.query(Document)
        .filter(
            Document.user_id == user_id
        )
        .all()
    )


def get_user_document(
    db: Session,
    user_id: int,
    category: str,
):
    return (
        db.query(Document)
        .filter(
            Document.user_id == user_id,
            Document.category == category,
        )
        .first()
    )


def get_document_url(
    db: Session,
    user_id: int,
    category: str,
):
    document = get_user_document(
        db,
        user_id,
        category,
    )

    if not document:
        return None

    return create_file_url(
        document.file_path
    )

   #here we have calling the update_document function which is callled before definng , this works in python bcz .
   #when file is executed python interpreter reads the whole file and then executes the code, 
   # so it can find the function definition even if it is defined after the call.
async def update_document(
    db: Session,
    user_id: int,
    category: str,
    details: dict,
    file: UploadFile | None = None,
):
    document = get_user_document(
        db,
        user_id,
        category,
    )

    if not document:
        raise ValueError(
            "Document not found"
        )

    validate_document_details(
        category,
        details,
    )

    old_file_path = document.file_path
    new_file_path = None

    try:
        # Update file only if new file provided
        if file:
            if file.content_type not in ALLOWED_FILE_TYPES:
                raise ValueError(
                    "Only PDF, JPG and PNG files are allowed"
                )

            file_content = await file.read()

            if not file_content:
                raise ValueError(
                    "Uploaded file is empty"
                )

            if len(file_content) > MAX_FILE_SIZE:
                raise ValueError(
                    "File size must be less than 5 MB"
                )

            new_file_path = create_storage_path(
                user_id,
                category,
                file.filename,
            )

            upload_file(
                file_content=file_content,
                storage_path=new_file_path,
                content_type=file.content_type,
            )

            document.file_name = file.filename
            document.file_type = file.content_type
            document.file_size = len(file_content)
            document.file_path = new_file_path

        # Update details
        for key, value in details.items():
            setattr(document, key, value)

        # Reset status back to submitted when new file or updated details are provided
        document.status = "submitted"

        db.commit()
        db.refresh(document)


        # Delete old file after DB update
        if new_file_path:
            delete_file(old_file_path)

        return document

    except Exception:
        db.rollback()

        # If new file was uploaded but DB update failed
        if new_file_path:
            delete_file(new_file_path)

        raise


def delete_document(
    db: Session,
    user_id: int,
    category: str,
):
    document = get_user_document(
        db,
        user_id,
        category,
    )

    if not document:
        raise ValueError(
            "Document not found"
        )

    file_path = document.file_path

    # Delete database row
    db.delete(document)
    db.commit()

    # Delete file from Supabase
    delete_file(file_path)

    return True