import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt

from app.db.session import SessionLocal

from app.core.config import settings
from app.core.config import settings
from app.models.user import User
from app.models.university import University
from app.schemas.user import UserCreate, UserRead
from app.utils.email import send_confirmation_email
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    email_domain = user.email.split("@")[-1]
    university = db.query(University).filter(University.email_domain == email_domain).first()

    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(hours=24)

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        nickname=user.nickname,
        hashed_password=hash_password(user.password),
        is_active=False,
        university_id=university.id if university else None,
        activation_token=token,
        activation_token_expiry=expiry
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    activation_link = f"{settings.BASE_URL}/auth/activate?token={token}" # В проде — заменить host!
    activation_link = f"http://localhost:8000/auth/activate?token={token}"  # В проде — заменить host!

    activation_link = f"{settings.BASE_URL}/auth/activate?token={token}" # В проде — заменить host!
    send_confirmation_email(new_user.email, activation_link)

    return new_user


@router.post("/login")
def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь ожидает подтверждения")

    token = create_access_token({"sub": str(user.id)})

    response = JSONResponse({
        "message": "Успешный вход",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "nickname": user.nickname,
            "is_admin": user.is_admin,
        }
    })
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="Lax",
        max_age=60 * 60 * 24,  # 1 день
        secure=False,  # В продакшне поставь True
        path="/"
    )
    return response


@router.post("/logout")
def logout():
    response = JSONResponse({"message": "Выход выполнен"})
    response.delete_cookie("access_token", path="/")
    return response


@router.get("/me", response_model=UserRead)
def get_me(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Неавторизован")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/activate")
def activate_account(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.activation_token == token).first()
    if not user:
        return {"ok": False, "message": "Некорректная или устаревшая ссылка активации"}
    if user.activation_token_expiry < datetime.utcnow():
        return {"ok": False, "message": "Срок действия ссылки истёк"}

    user.is_active = True
    user.activation_token = None
    user.activation_token_expiry = None
    db.commit()
    # Можешь редиректить на страницу логина с флагом или просто сообщение
    return RedirectResponse(url="/auth/login?activated=1")
    # или: return {"ok": True, "message": "Аккаунт успешно активирован"}


@router.get("/check")
def check_auth(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Не авторизован")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return {"ok": True}
