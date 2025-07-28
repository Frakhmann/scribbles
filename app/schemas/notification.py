from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class NotificationBase(BaseModel):
    message: str
    post_id: Optional[int]

class NotificationCreate(NotificationBase):
    recipient_id: int
    sender_id: Optional[int]

class NotificationOut(NotificationBase):
    id: int
    recipient_id: int
    sender_id: Optional[int]
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True
