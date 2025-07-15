from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from app.auth.dependencies import get_current_user
from app.core.templates import templates
from app.db.session import SessionLocal
from app.models.section import Section
from app.models.university import University
from app.schemas.section import SectionCreate, SectionRead
from app.utils.security import get_admin_user

router = APIRouter(prefix="/sections", tags=["sections"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=SectionRead)
def create_section(section_in: SectionCreate, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    university = db.query(University).filter(University.id == section_in.university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail="Университет не найден")
    section = Section(**section_in.dict())
    db.add(section)
    db.commit()
    db.refresh(section)
    return section

@router.get("/", response_model=List[SectionRead])
def get_all_sections(db: Session = Depends(get_db)):
    return db.query(Section).all()

@router.get("/by_university/{university_id}", response_model=List[SectionRead])
def get_sections_by_university(university_id: int, db: Session = Depends(get_db)):
    return db.query(Section).filter(Section.university_id == university_id).all()

@router.get("/university/{university_id}/sections", response_class=HTMLResponse)
def university_sections(
    university_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    university = db.query(University).filter(University.id == university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail="Университет не найден")
    sections = db.query(Section).filter(Section.university_id == university_id).all()
    return templates.TemplateResponse(
        "sections.html",
        {
            "request": request,
            "university": university,
            "sections": sections,
            "current_user": current_user,
        },
    )

@router.get("/universities/{university_id}/sections", response_class=HTMLResponse)
def university_sections_alias(
    university_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return university_sections(
        university_id=university_id,
        request=request,
        db=db,
        current_user=current_user
    )
