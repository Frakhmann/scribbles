from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.notification import NotificationOut, NotificationCreate
from app.crud import crud_notification
from app.auth.dependencies import get_current_user
from app.core.templates import templates

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/page", response_class=HTMLResponse)
def notifications_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse("coming_soon.html", {
        "request": request,
        "title": "Раздел уведомлений",
        "desc": "В ближайшем обновлении здесь появятся уведомления о новых событиях и активностях.",
        "current_user": current_user,
    })

@router.get("/", response_model=List[NotificationOut])
def get_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud_notification.get_user_notifications(db, user_id=current_user.id)

@router.post("/", response_model=NotificationOut)
def create_notification(notif: NotificationCreate, db: Session = Depends(get_db)):
    return crud_notification.create_notification(db, notif)

@router.put("/{notif_id}/read", response_model=NotificationOut)
def mark_notification_as_read(notif_id: int, db: Session = Depends(get_db)):
    return crud_notification.mark_as_read(db, notif_id)
