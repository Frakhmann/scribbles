from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.models import like as like_model
from app.schemas import like as like_schema
from app.auth.dependencies import get_current_user
from app.models.user import User
from sqlalchemy import func

router = APIRouter(prefix="/likes", tags=["Likes"])

@router.post("/")
def toggle_like(
    like_data: like_schema.LikeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    like = db.query(like_model.Like).filter_by(
        user_id=current_user.id,
        post_id=like_data.post_id
    ).first()

    if like:
        db.delete(like)
        db.commit()
        total_likes = db.query(func.count(like_model.Like.id)).filter_by(post_id=like_data.post_id).scalar()
        return {"liked": False, "likes_count": total_likes}

    try:
        new_like = like_model.Like(
            user_id=current_user.id,
            post_id=like_data.post_id
        )
        db.add(new_like)
        db.commit()
        total_likes = db.query(func.count(like_model.Like.id)).filter_by(post_id=like_data.post_id).scalar()
        return {"liked": True, "likes_count": total_likes}

    except IntegrityError:
        db.rollback()
        total_likes = db.query(func.count(like_model.Like.id)).filter_by(post_id=like_data.post_id).scalar()
        return {"liked": True, "likes_count": total_likes}

# ⬇️ Новый эндпоинт для получения всех постов, залайканных текущим юзером
@router.get("/user-liked-posts")
def get_user_liked_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    liked = db.query(like_model.Like.post_id).filter(like_model.Like.user_id == current_user.id).all()
    post_ids = [post_id for (post_id,) in liked]
    return post_ids
