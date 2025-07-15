from pydantic import BaseModel

class LikeCreate(BaseModel):
    post_id: int

class LikeOut(BaseModel):
    liked: bool  # true если добавили, false если убрали
    