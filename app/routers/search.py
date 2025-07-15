from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.core.templates import templates
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/", response_class=HTMLResponse)
@router.get("/page", response_class=HTMLResponse)
def search_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse("coming_soon.html", {
        "request": request,
        "title": "Поиск по Scribbles",
        "desc": "Функция поиска постов появится в одном из следующих релизов.",
        "current_user": current_user,
    })
