from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Document, User
from app.services.seed_data import reset_demo, seed_demo


router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/seed")
def seed(session: Session = Depends(get_session)):
    return seed_demo(session)


@router.delete("/reset")
def reset(session: Session = Depends(get_session)):
    reset_demo(session)
    return {"status": "reset"}


@router.get("/status")
def status(session: Session = Depends(get_session)):
    count = len(session.scalars(select(Document)).all())
    return {"seeded": bool(session.get(User, "demo-user") and count), "documents_count": count}

