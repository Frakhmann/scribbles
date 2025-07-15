from pydantic import BaseModel, EmailStr
from typing import Optional

# Базовая схема для всех операций
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    nickname: str

# Используется при создании нового пользователя
class UserCreate(UserBase):
    password: str

# Используется при авторизации
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Токен доступа
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Ответ при запросе информации о пользователе
class UserRead(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    university_id: Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True
