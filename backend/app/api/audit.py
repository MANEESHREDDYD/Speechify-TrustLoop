from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas import ManualAuditRequest
from app.services.manual_audit import run_manual_audit


router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.post("/manual")
def manual_audit(request: ManualAuditRequest, session: Session = Depends(get_session)):
    if not request.source_title.strip():
        raise HTTPException(422, "Source title must not be empty")
    if not request.source_text.strip():
        raise HTTPException(422, "Source text must not be empty")
    if not request.generated_text.strip():
        raise HTTPException(422, "Generated output must not be empty")
    try:
        return run_manual_audit(
            session,
            user_id=request.user_id,
            source_title=request.source_title,
            source_text=request.source_text,
            output_type=request.output_type,
            generated_text=request.generated_text,
        )
    except Exception as exc:
        session.rollback()
        raise HTTPException(500, f"Manual audit failed: {exc}") from exc
