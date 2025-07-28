from fastapi import (
    APIRouter, Depends, HTTPException, status, Query, Request,
    Form, UploadFile, File
)
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from sqlalchemy import func
from jose import JWTError, jwt

from app.core.config import settings
from app.db.session import SessionLocal
from app.models import Post, User, University, Section, Like
from app.schemas.post import PostCreate, PostRead, PostUpdate
from app.schemas.report import ReportCreate
from app.crud import crud_report
from app.utils.security import get_current_user
from app.auth.dependencies import get_current_user_optional, get_current_user
from app.core.templates import templates
from app.utils.b2_upload import upload_file_to_b2
import uuid

from app.models.post import Post
from app.models.user import User
from app.models.university import University
from app.models.section import Section


router = APIRouter(prefix="/posts", tags=["posts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📌 API: Создание поста
@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Только активные пользователи могут создавать посты")

    university = db.query(University).filter(University.id == post_in.university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail="Университет не найден")

    section = db.query(Section).filter(Section.id == post_in.section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Раздел не найден")

    if section.university_id != post_in.university_id:
        raise HTTPException(status_code=400, detail="Раздел не принадлежит указанному университету")

    post = Post(**post_in.dict(), user_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)

    setattr(post, "likes_count", 0)
    return post

# 📌 API: Получение всех постов с фильтрацией
@router.get("/", response_model=List[PostRead])
def get_all_posts(
    university_id: Optional[int] = Query(None),
    section_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Post)

    if university_id:
        query = query.filter(Post.university_id == university_id)
    if section_id:
        query = query.filter(Post.section_id == section_id)

    posts = query.order_by(Post.created_at.desc()).all()

    for post in posts:
        likes = db.query(Like).filter_by(post_id=post.id).count()
        setattr(post, "likes_count", likes)

    return posts

@router.get("/batch-like-counts")
def batch_like_counts(
    ids: str = Query(..., alias="ids"),
    db: Session = Depends(get_db)
):
    print("DEBUG IDS:", ids)
    id_list = [int(x) for x in ids.split(",") if x.strip().isdigit()]
    print("DEBUG ID_LIST:", id_list)
    counts = (
        db.query(Like.post_id, func.count(Like.id))
        .filter(Like.post_id.in_(id_list))
        .group_by(Like.post_id)
        .all()
    )
    result = {post_id: count for post_id, count in counts}
    for i in id_list:
        if i not in result:
            result[i] = 0
    print("DEBUG RESULT:", result)
    return result

# 📌 API: Обновление поста
@router.put("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    post_in: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    if post.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав для редактирования поста")

    if post_in.section_id:
        section = db.query(Section).filter(Section.id == post_in.section_id).first()
        if not section or section.university_id != post.university_id:
            raise HTTPException(status_code=400, detail="Раздел не найден или не принадлежит вузу поста")
        post.section_id = post_in.section_id

    for field, value in post_in.dict(exclude_unset=True).items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)

    likes = db.query(Like).filter_by(post_id=post.id).count()
    setattr(post, "likes_count", likes)

    return post

# 📌 API: Удаление поста
@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    if post.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав для удаления поста")

    # Сохраняем данные ДО удаления!
    section_id = post.section_id
    university_id = post.university_id

    db.delete(post)
    db.commit()

    # Строим редирект на нужную ленту после удаления
    redirect_url = f"/sections/{section_id}/posts?from=/universities/{university_id}/sections"
    return {"redirect_url": redirect_url}


@router.delete("/{post_id}")
def delete_post_api(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    if post.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав для удаления поста")
    
    university_id = post.university_id
    section_id = post.section_id

    db.delete(post)
    db.commit()

    return {"redirect_url": f"/sections/{section_id}/posts"}


# 🧾 HTML: Лента постов
@router.get("/feed", response_class=HTMLResponse)
def post_feed(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    for post in posts:
        likes = db.query(Like).filter_by(post_id=post.id).count()
        setattr(post, "likes_count", likes)
        liked = db.query(Like).filter_by(post_id=post.id, user_id=current_user.id).first() is not None
        setattr(post, "liked_by_me", liked)

    response = templates.TemplateResponse("index.html", {
        "request": request,
        "posts": posts,
        "current_user": current_user
    })
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response

# 🧾 HTML: Форма создания поста
@router.get("/create", response_class=HTMLResponse)
def create_post_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    universities = db.query(University).all()
    sections = db.query(Section).all()
    sections_by_university = {}
    for s in sections:
        sections_by_university.setdefault(s.university_id, []).append({
            "id": s.id,
            "name": s.name
        })

    return templates.TemplateResponse("create_post.html", {
        "request": request,
        "universities": universities,
        "sections_by_university": sections_by_university,
        "current_user": current_user 
    })

# 🧾 HTML: Отправка формы
@router.post("/create", response_class=HTMLResponse)
def create_post_from_form(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    university_id: int = Form(...),
    section_id: int = Form(...),
    token: str = Form(...),
    media: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Неверный токен")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь не найден или неактивен")

    media_url = None
    if media:
        ext = media.filename.split('.')[-1]
        filename = f"posts/{uuid.uuid4()}.{ext}"
        media_url = upload_file_to_b2(media.file, filename, media.content_type)

    new_post = Post(
        title=title,
        content=content,
        university_id=university_id,
        section_id=section_id,
        user_id=user.id,
        media_url=media_url
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return RedirectResponse(
        url=f"/posts/{new_post.id}?from=/sections/{section_id}/posts?from=/universities/{university_id}/sections",
        status_code=303
    )

# 🧾 HTML: Страница одного поста
@router.get("/{post_id}", response_class=HTMLResponse)
def view_post(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    is_author = post.user_id == current_user.id
    is_admin = current_user.is_admin

    likes_count = db.query(Like).filter(Like.post_id == post.id).count()
    setattr(post, "likes_count", likes_count)
    liked_by_me = db.query(Like).filter_by(post_id=post.id, user_id=current_user.id).first() is not None
    setattr(post, "liked_by_me", liked_by_me)

    response = templates.TemplateResponse("post_detail.html", {
        "request": request,
        "post": post,
        "current_user": current_user,
        "is_author": is_author,
        "is_admin": is_admin,
        "liked_by_me": liked_by_me,
    })
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response

@router.get("/university/{university_id}", response_class=HTMLResponse)
def post_feed_by_university(
    university_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts = db.query(Post).filter(Post.university_id == university_id).order_by(Post.created_at.desc()).all()
    for post in posts:
        likes = db.query(Like).filter_by(post_id=post.id).count()
        setattr(post, "likes_count", likes)
        liked = db.query(Like).filter_by(post_id=post.id, user_id=current_user.id).first() is not None
        setattr(post, "liked_by_me", liked)

    class SectionObj:
        def __init__(self, university_id):
            self.name = "Общая лента"
            self.university_id = university_id
    section = SectionObj(university_id)

    response = templates.TemplateResponse("section_posts.html", {
        "request": request,
        "posts": posts,
        "current_user": current_user,
        "section": section
    })
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response

@router.post("/report")
def report_post(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Только активные пользователи могут жаловаться")
    report = crud_report.create_report(db, report_in, current_user.id)
    return {"detail": "Report submitted"}



