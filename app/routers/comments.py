from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead
from app.utils.security import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/post/{post_id}", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def add_comment(post_id: int, comment_in: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    comment = Comment(
        post_id=post.id,
        user_id=current_user.id,
        content=comment_in.content,
        is_anonymous=comment_in.is_anonymous or False
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/post/{post_id}", response_model=List[CommentRead])
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at).all()


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    if comment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет прав для удаления")

    db.delete(comment)
    db.commit()
