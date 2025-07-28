from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.university import University
from app.auth.dependencies import get_current_user
from app.core.templates import templates

router = APIRouter(prefix="/universities", tags=["universities"])

@router.get("/", response_class="HTMLResponse")
def university_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # Получаем все университеты
    universities = db.query(University).order_by(University.name).all()

    # Университет пользователя — первым
    user_university = None
    other_universities = []
    if current_user and current_user.university_id:
        for u in universities:
            if u.id == current_user.university_id:
                user_university = u
            else:
                other_universities.append(u)
    else:
        other_universities = universities

    return templates.TemplateResponse(
        "universities.html",
        {
            "request": request,
            "user_university": user_university,
            "other_universities": other_universities,
            "current_user": current_user,
        },
    )
