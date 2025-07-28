from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentCreate(BaseModel):
    content: str
    is_anonymous: Optional[bool] = False

class CommentRead(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    is_anonymous: bool
    created_at: datetime
    likes_count: int

    class Config:
        from_attributes= True
