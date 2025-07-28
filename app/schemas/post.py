from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    media_url: Optional[str] = None
    university_id: int
    section_id: int


class PostCreate(PostBase):
    pass


class PostRead(PostBase):
    id: int
    user_id: int
    created_at: datetime
    likes_count: int  # вычисляется вручную

    class Config:
        orm_mode = True


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    media_url: Optional[str] = None
    section_id: Optional[int] = None

    class Config:
        from_attributes = True

