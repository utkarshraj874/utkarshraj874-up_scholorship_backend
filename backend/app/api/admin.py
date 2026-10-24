from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db, get_current_admin
from backend.app.core.storage import create_file_url
from backend.app.models.user import User
from backend.app.models.profile import Profile
from backend.app.models.documents import Document
from backend.app.models.notification import Notification
from backend.app.models.help_query import HelpQuery
from backend.app.schema.documents import DocumentResponse, DocumentReviewRequest


router = APIRouter(
    prefix="/admin",
    tags=["Admin / Scholarship Coordinator"],
)


@router.get("/dashboard-stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    Get summary statistics for the scholarship coordinator dashboard.
    """
    total_students = db.query(User).filter(User.role == "student").count()
    total_documents = db.query(Document).count()
    verified_documents = db.query(Document).filter(Document.status == "verified").count()
    correction_required = db.query(Document).filter(Document.status == "correction_required").count()
    open_queries = db.query(HelpQuery).filter(HelpQuery.status == "open").count()

    return {
        "total_students": total_students,
        "total_documents": total_documents,
        "verified_documents": verified_documents,
        "correction_required": correction_required,
        "open_queries": open_queries,
    }


@router.get("/students")
def get_all_students(
    search: str | None = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    List all students along with their profile summary and document counts.
    """
    query = db.query(User).filter(User.role == "student")
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (User.name.ilike(s)) | (User.email.ilike(s))
        )

    students = query.order_by(User.id.desc()).all()

    result = []
    for s in students:
        profile = db.query(Profile).filter(Profile.user_id == s.id).first()
        docs = db.query(Document).filter(Document.user_id == s.id).all()

        uploaded_count = len(docs)
        verified_count = sum(1 for d in docs if d.status == "verified")
        correction_count = sum(1 for d in docs if d.status == "correction_required")

        result.append({
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "role": s.role,
            "profile": {
                "registration_no": profile.registration_no if profile else None,
                "department": profile.department if profile else None,
                "semester": profile.semester if profile else None,
                "family_income": profile.family_income if profile else None,
                "category": profile.category if profile else None,
                "phone_no": profile.phone_no if profile else None,
                "tenth_percentage": profile.tenth_percentage if profile else None,
                "twelfth_percentage": profile.twelfth_percentage if profile else None,
            } if profile else None,
            "documents_count": uploaded_count,
            "verified_count": verified_count,
            "correction_count": correction_count,
        })

    return result


@router.get("/students/{student_id}/documents")
def get_student_documents(
    student_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    Get all documents uploaded by a specific student, complete with signed view URLs.
    """
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    profile = db.query(Profile).filter(Profile.user_id == student_id).first()
    docs = db.query(Document).filter(Document.user_id == student_id).all()

    documents_with_urls = []
    for d in docs:
        doc_dict = DocumentResponse.model_validate(d).model_dump()
        try:
            doc_dict["file_url"] = create_file_url(d.file_path, expires_in=7200)
        except Exception:
            doc_dict["file_url"] = None
        documents_with_urls.append(doc_dict)

    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "email": student.email,
        },
        "profile": {
            "registration_no": profile.registration_no if profile else None,
            "department": profile.department if profile else None,
            "semester": profile.semester if profile else None,
            "family_income": profile.family_income if profile else None,
            "category": profile.category if profile else None,
            "phone_no": profile.phone_no if profile else None,
            "tenth_percentage": profile.tenth_percentage if profile else None,
            "twelfth_percentage": profile.twelfth_percentage if profile else None,
        } if profile else None,
        "documents": documents_with_urls,
    }


@router.post("/documents/{document_id}/review", response_model=DocumentResponse)
def review_document(
    document_id: int,
    data: DocumentReviewRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    Admin reviews a document: approve as 'verified' or request 'correction_required' with suggestions.
    Sends a notification to the student.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    allowed_statuses = ["verified", "correction_required", "submitted"]
    if data.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed_statuses}")

    doc.status = data.status
    doc.admin_remarks = data.admin_remarks.strip() if data.admin_remarks else None
    doc.verified_at = datetime.utcnow()
    doc.updated_at = datetime.utcnow()

    # Generate appropriate notification for student
    readable_category = doc.category.replace("_", " ").title()
    if data.status == "correction_required":
        notif = Notification(
            user_id=doc.user_id,
            title=f"⚠️ Action Required: {readable_category}",
            message=f"Scholarship Coordinator suggestion: {data.admin_remarks or 'Please re-check your uploaded document and details.'}",
            category=doc.category,
        )
        db.add(notif)
    elif data.status == "verified":
        notif = Notification(
            user_id=doc.user_id,
            title=f"✅ Document Verified: {readable_category}",
            message=f"Your {readable_category} has been verified and approved by the Scholarship Coordinator.",
            category=doc.category,
        )
        db.add(notif)

    db.commit()
    db.refresh(doc)

    res = DocumentResponse.model_validate(doc)
    try:
        res.file_url = create_file_url(doc.file_path, expires_in=7200)
    except Exception:
        res.file_url = None
    return res
