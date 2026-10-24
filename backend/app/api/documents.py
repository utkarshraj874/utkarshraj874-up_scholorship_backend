from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db, get_current_user_optional
from backend.app.models.user import User
from backend.app.schema.documents import (
    DocumentCreate,
    DocumentResponse,
)
from backend.app.services.document_services import (
    create_document,
    get_user_documents,
    get_user_document,
    get_document_url,
    update_document,
    delete_document,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


def resolve_user_id(user_id: int | None, current_user: User | None) -> int:
    if current_user:
        return current_user.id
    if user_id:
        return user_id
    raise HTTPException(
        status_code=401,
        detail="Authentication required or user_id must be provided",
    )


# -------------------------------------------------
# CREATE / UPLOAD DOCUMENT
# -------------------------------------------------

@router.post(
    "/",
    response_model=DocumentResponse,
)
async def upload_document(
    user_id: int | None = Form(None),
    category: str = Form(...),
    details: str = Form("{}"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    actual_user_id = resolve_user_id(user_id, current_user)

    try:
        import json

        document_details = json.loads(details)

        document_data = DocumentCreate(
            category=category,
            **document_details,
        )

        document = await create_document(
            db=db,
            user_id=actual_user_id,
            category=category,
            details=document_data.model_dump(
                exclude={"category"}
            ),
            file=file,
        )

        return document

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# -------------------------------------------------
# GET ALL USER DOCUMENTS
# -------------------------------------------------

@router.get(
    "/",
    response_model=list[DocumentResponse],
)
def get_documents(
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    actual_user_id = resolve_user_id(user_id, current_user)
    return get_user_documents(
        db=db,
        user_id=actual_user_id,
    )


# -------------------------------------------------
# GET ONE DOCUMENT
# -------------------------------------------------

@router.get(
    "/{category}",
    response_model=DocumentResponse,
)
def get_document(
    category: str,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    actual_user_id = resolve_user_id(user_id, current_user)
    document = get_user_document(
        db=db,
        user_id=actual_user_id,
        category=category,
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


# -------------------------------------------------
# GET PRIVATE FILE URL
# -------------------------------------------------

@router.get(
    "/{category}/file",
)
def view_document_file(
    category: str,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    actual_user_id = resolve_user_id(user_id, current_user)
    url = get_document_url(
        db=db,
        user_id=actual_user_id,
        category=category,
    )

    if not url:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "category": category,
        "file_url": url,
    }


# -------------------------------------------------
# UPDATE DOCUMENT
# -------------------------------------------------

@router.put(
    "/{category}",
    response_model=DocumentResponse,
)
async def update_document_api(
    category: str,
    user_id: int | None = Form(None),
    details: str = Form("{}"),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    actual_user_id = resolve_user_id(user_id, current_user)
    try:
        import json

        document_details = json.loads(details)

        document_data = DocumentCreate(
            category=category,
            **document_details,
        )

        document = await update_document(
            db=db,
            user_id=actual_user_id,
            category=category,
            details=document_data.model_dump(
                exclude={"category"}
            ),
            file=file,
        )

        return document

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# -------------------------------------------------
# DELETE DOCUMENT
# -------------------------------------------------

@router.delete(
    "/{category}",
)
def remove_document(
    category: str,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    actual_user_id = resolve_user_id(user_id, current_user)
    try:
        delete_document(
            db=db,
            user_id=actual_user_id,
            category=category,
        )

        return {
            "message": "Document deleted successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
