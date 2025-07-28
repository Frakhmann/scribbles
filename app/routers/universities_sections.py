from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.section import Section
from app.models.post import Post
from app.models.like import Like
from app.models.university import University
from app.auth.dependencies import get_current_user
from app.core.templates import templates

router = APIRouter(tags=["universities_sections"])
router = APIRouter(tags=["sections_html"])

@router.get("/universities/{university_id}/sections", response_class=HTMLResponse)
def university_sections(
    university_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    university = db.query(University).filter(University.id == university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail="Университет не найден")
    sections = db.query(Section).filter(Section.university_id == university_id).all()
    return templates.TemplateResponse(
        "sections.html",
        {
            "request": request,
            "university": university,
            "sections": sections,
            "current_user": current_user,
        },
    )

@router.get("/sections/{section_id}/posts", response_class=HTMLResponse)
def section_posts(
    section_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Раздел не найден")

    posts = db.query(Post).filter(Post.section_id == section_id).order_by(Post.created_at.desc()).all()
    
    # 1. Получаем ID всех постов, которые лайкнул текущий пользователь
    liked_post_ids = set()
    if current_user:
        liked = db.query(Like.post_id).filter(Like.user_id == current_user.id).all()
        liked_post_ids = {post_id for (post_id,) in liked}
    
    # 2. Для каждого поста ставим флаги и считаем лайки
    for post in posts:
        post.likes_count = db.query(Like).filter_by(post_id=post.id).count()
        post.user_liked = post.id in liked_post_ids  # поле именно такое! (user_liked)

    return templates.TemplateResponse(
        "section_posts.html",
        {
            "request": request,
            "section": section,
            "posts": posts,
            "current_user": current_user,
        }
    )

