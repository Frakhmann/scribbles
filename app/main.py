from fastapi import FastAPI, Depends, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from fastapi.exceptions import RequestValidationError

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.post import Post
from app.models.like import Like
from app.models.user import User

from starlette.exceptions import HTTPException as StarletteHTTPException


from app.routers import auth, users, posts, sections, comments, like, notification, universities, universities_sections, search, admin



app = FastAPI(
    title="Scribbles Forum",
    description="SCRIBBLES",
    version="0.1.0",
)

# 📦 Подключение маршрутов
app.include_router(auth.router, prefix="/auth")
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(sections.router)
app.include_router(comments.router)
app.include_router(like.router)
app.include_router(notification.router)
app.include_router(universities.router)
app.include_router(universities_sections.router)
app.include_router(search.router)
app.include_router(admin.router)

# 🌐 Статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 🧩 Шаблоны Jinja2
templates = Jinja2Templates(directory="app/templates")

# 🏠 Главная страница (лента постов)
@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    posts = (
        db.query(Post)
        .options(joinedload(Post.user))
        .order_by(Post.created_at.desc())
        .all()
    )

    liked_post_ids = set()
    if current_user:
        liked = db.query(Like.post_id).filter(Like.user_id == current_user.id).all()
        liked_post_ids = {post_id for (post_id,) in liked}

    for post in posts:
        post.likes_count = db.query(Like).filter_by(post_id=post.id).count()
        post.liked_by_me = post.id in liked_post_ids

    response = templates.TemplateResponse("index.html", {
        "request": request,
        "posts": posts,
        "current_user": current_user
    })
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    accept = request.headers.get("accept", "")
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        if "text/html" in accept:
            return RedirectResponse(url="/auth/login")
        else:
            return JSONResponse(status_code=401, content={"detail": "Неавторизован"})
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        # Отдельно для 404 (иначе твой кастомный не вызовется)
        return await not_found_handler(request, exc)
    else:
        # Для остальных ошибок: стандартное поведение
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# 404 Not Found (рендерим шаблон)
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
