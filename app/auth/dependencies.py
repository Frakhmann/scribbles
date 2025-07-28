from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from jose import JWTError, jwt

from app.db.session import get_db
from app.models.user import User
from app.core.config import settings


def get_current_user(
        request: Request,
        db: Session = Depends(get_db)
) -> User:
    print("🍪 Куки:", request.cookies)

    token = request.cookies.get("access_token")
    if not token:
        print("🚫 Кука отсутствует")
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
        print("🔓 user_id из токена:", user_id)
    except (JWTError, TypeError, ValueError) as e:
        print("❌ Ошибка в JWT:", e)
        raise HTTPException(status_code=401, detail="Неверный токен")

    user = db.query(User).filter(User.id == user_id).first()
    print("👤 Найденный пользователь:", user)

    if not user:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user




def get_current_user_optional(
        request: Request,
        db: Session = Depends(get_db)
) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        return None

    return db.query(User).filter(User.id == user_id).first()
