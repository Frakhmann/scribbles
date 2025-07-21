from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.utils.password import verify_password  # функция сравнения пароля
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin", tags=["Admin Login"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request, "error": None})

@router.post("/login", response_class=HTMLResponse)
def admin_login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_admin or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("admin/login.html", {"request": request, "error": "Неверный логин или пароль"})
    request.session["admin_user_id"] = user.id
    return RedirectResponse(url="/admin/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=302)
