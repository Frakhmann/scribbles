from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional

class ReportCreate(BaseModel):
    post_id: int
    reason: constr(min_length=1, max_length=200)

class ReportRead(BaseModel):
    id: int
    post_id: int
    user_id: Optional[int]
    reason: str
    created_at: datetime

    class Config:
        orm_mode = True
