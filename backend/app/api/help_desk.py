from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db, get_current_user, get_current_admin
from backend.app.models.user import User
from backend.app.models.help_query import HelpQuery
from backend.app.models.notification import Notification
from backend.app.schema.help_query import (
    HelpQueryCreate,
    HelpQueryReply,
    HelpQueryResponse,
)


router = APIRouter(
    prefix="/help-desk",
    tags=["Help Desk"],
)


@router.post("/", response_model=HelpQueryResponse)
def create_help_query(
    data: HelpQueryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Student submits a query or help request to the scholarship coordinator.
    """
    query = HelpQuery(
        student_id=current_user.id,
        subject=data.subject.strip(),
        message=data.message.strip(),
        status="open",
    )
    db.add(query)
    db.commit()
    db.refresh(query)

    return HelpQueryResponse(
        id=query.id,
        student_id=query.student_id,
        student_name=current_user.name,
        student_email=current_user.email,
        subject=query.subject,
        message=query.message,
        status=query.status,
        admin_reply=query.admin_reply,
        replied_at=query.replied_at,
        created_at=query.created_at,
        updated_at=query.updated_at,
    )


@router.get("/my-queries", response_model=list[HelpQueryResponse])
def get_my_queries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Student views all their help queries and responses.
    """
    queries = (
        db.query(HelpQuery)
        .filter(HelpQuery.student_id == current_user.id)
        .order_by(HelpQuery.created_at.desc())
        .all()
    )

    return [
        HelpQueryResponse(
            id=q.id,
            student_id=q.student_id,
            student_name=current_user.name,
            student_email=current_user.email,
            subject=q.subject,
            message=q.message,
            status=q.status,
            admin_reply=q.admin_reply,
            replied_at=q.replied_at,
            created_at=q.created_at,
            updated_at=q.updated_at,
        )
        for q in queries
    ]


@router.get("/all", response_model=list[HelpQueryResponse])
def get_all_queries_for_admin(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    Admin views all queries submitted by students.
    """
    query_builder = db.query(HelpQuery)
    if status and status != "all":
        query_builder = query_builder.filter(HelpQuery.status == status)

    queries = query_builder.order_by(HelpQuery.created_at.desc()).all()

    results = []
    for q in queries:
        student = db.query(User).filter(User.id == q.student_id).first()
        results.append(
            HelpQueryResponse(
                id=q.id,
                student_id=q.student_id,
                student_name=student.name if student else "Unknown",
                student_email=student.email if student else "Unknown",
                subject=q.subject,
                message=q.message,
                status=q.status,
                admin_reply=q.admin_reply,
                replied_at=q.replied_at,
                created_at=q.created_at,
                updated_at=q.updated_at,
            )
        )
    return results


@router.post("/{query_id}/reply", response_model=HelpQueryResponse)
def reply_to_help_query(
    query_id: int,
    data: HelpQueryReply,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    Admin replies to a student query, marks it resolved, and notifies the student.
    """
    query = db.query(HelpQuery).filter(HelpQuery.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Help query not found")

    reply_text = data.admin_reply.strip()
    query.admin_reply = reply_text
    query.status = "resolved"
    query.replied_at = datetime.utcnow()
    query.updated_at = datetime.utcnow()

    # Create a notification for the student
    notif = Notification(
        user_id=query.student_id,
        title=f"Coordinator Replied to your Query: {query.subject[:40]}",
        message=f"Scholarship Coordinator ({current_admin.name}) answered: {reply_text}",
        category="help_query",
    )
    db.add(notif)

    db.commit()
    db.refresh(query)

    student = db.query(User).filter(User.id == query.student_id).first()
    return HelpQueryResponse(
        id=query.id,
        student_id=query.student_id,
        student_name=student.name if student else "Unknown",
        student_email=student.email if student else "Unknown",
        subject=query.subject,
        message=query.message,
        status=query.status,
        admin_reply=query.admin_reply,
        replied_at=query.replied_at,
        created_at=query.created_at,
        updated_at=query.updated_at,
    )
