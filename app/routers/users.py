from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import SessionLocal
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like
from app.schemas.user import UserRead
from app.utils.security import get_current_user, get_admin_user
from app.auth.dependencies import get_current_user_optional, get_current_user
from app.db.session import get_db
from app.core.templates import templates

from app.utils.b2_upload import upload_file_to_b2
import uuid

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users", response_model=list[UserRead], dependencies=[Depends(get_admin_user)])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/users/pending", response_model=list[UserRead], dependencies=[Depends(get_admin_user)])
def get_pending_users(db: Session = Depends(get_db)):
    return db.query(User).filter(User.is_active == False).all()


@router.post("/users/{user_id}/approve", response_model=UserRead)
def approve_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.get("/profile/{nickname}", response_class=HTMLResponse)
def user_profile(
        nickname: str,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.nickname == nickname).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    posts = (
        db.query(Post)
        .filter(Post.user_id == user.id)
        .order_by(Post.created_at.desc())
        .all()
    )

    comments = (
        db.query(Comment)
        .filter(Comment.user_id == user.id)
        .order_by(Comment.created_at.desc())
        .all()
    )

    liked_posts = (
        db.query(Post)
        .join(Like, Like.post_id == Post.id)
        .filter(Like.user_id == user.id)
        .all()
    )

    liked_comments = (
        db.query(Comment)
        .join(Like, Like.comment_id == Comment.id)
        .filter(Like.user_id == user.id)
        .all()
    )

    # 🔧 Добавляем данные для отображения карточек
    for post in posts + liked_posts:
        post.likes_count = db.query(Like).filter(Like.post_id == post.id).count()
        post.liked_by_me = (
            db.query(Like)
            .filter(Like.post_id == post.id, Like.user_id == current_user.id if current_user else -1)
            .count() > 0
        )
        post.comments_count = len(post.comments) if hasattr(post, "comments") else 0

    response = templates.TemplateResponse("profile.html", {
        "request": request,
        "user_profile": user,
        "posts": posts,
        "comments": comments,
        "liked_posts": liked_posts,
        "liked_comments": liked_comments,
        "current_user": current_user
    })
    response.headers["Cache-Control"]= "no-store, no-cache, must-revalidate"
    return response
    
@router.post("/profile/avatar")
async def upload_avatar(
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ext = avatar.filename.split('.')[-1]
    filename = f"avatars/{current_user.id}_{uuid.uuid4()}.{ext}"
    url = upload_file_to_b2(avatar.file, filename, avatar.content_type)

    current_user.avatar_url = url
    db.commit()
    db.refresh(current_user)

    return {"avatar_url": url}
