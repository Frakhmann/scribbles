from fastapi import APIRouter, Request, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.section import Section
from app.models.post import Post
from app.models.user import User
from fastapi.templating import Jinja2Templates
from app.models.university import University
from app.crud import crud_report
from app.models.report import Report

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="app/templates")

def get_current_admin_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("admin_user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated (admin)")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not an admin")
    return user

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    inactive_users = db.query(User).filter(User.is_active == False).count()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": current_user,
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "active": "dashboard"
    })


@router.get("/users", response_class=HTMLResponse)
def admin_users_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    users = db.query(User).order_by(User.id.desc()).all()
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "user": current_user,
        "users": users,
        "active": "users"  
    })

@router.post("/users/activate")
def admin_activate_user(
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/users/deactivate")
def admin_deactivate_user(
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/users/delete")
def admin_delete_user(
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/users/grant_admin")
def admin_grant_admin(
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = True
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/users/revoke_admin")
def admin_revoke_admin(
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = False
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)



@router.get("/universities", response_class=HTMLResponse)
def admin_universities_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    error: str = Query(None)
):
    universities = db.query(University).order_by(University.id.desc()).all()
    return templates.TemplateResponse("admin/universities.html", {
        "request": request,
        "user": current_user,
        "universities": universities,
        "active": "universities",
        "error": error
    })

@router.post("/universities/add")
def admin_universities_add(
    name: str = Form(...),
    email_domain: str = Form(...),
    image_url: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    university = University(name=name, email_domain=email_domain, image_url=image_url)
    db.add(university)
    db.commit()
    return RedirectResponse(url="/admin/universities", status_code=303)



@router.post("/universities/delete")
def admin_universities_delete(
    university_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    university = db.query(University).filter(University.id == university_id).first()
    if university:
        has_sections = db.query(Section).filter(Section.university_id == university.id).first()
        has_posts = db.query(Post).filter(Post.university_id == university.id).first()
        has_users = db.query(User).filter(User.university_id == university.id).first()
        if has_sections or has_posts or has_users:
            # Вместо raise — редирект на страницу с GET-параметром error
            error_msg = "Сначала удалите все секции, посты и пользователей, связанные с этим университетом."
            return RedirectResponse(
                url=f"/admin/universities?error={error_msg}",
                status_code=303
            )
        db.delete(university)
        db.commit()
    return RedirectResponse(url="/admin/universities", status_code=303)


#-----------------------------------------------

@router.get("/sections", response_class=HTMLResponse)
def admin_sections_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    error: str = Query(None)
):
    sections = db.query(Section).order_by(Section.id.desc()).all()
    universities = db.query(University).order_by(University.name).all()
    return templates.TemplateResponse("admin/sections.html", {
        "request": request,
        "user": current_user,
        "sections": sections,
        "universities": universities,
        "active": "sections",
        "error": error,
    })

@router.post("/sections/add")
def admin_sections_add(
    name: str = Form(...),
    university_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    section = Section(name=name, university_id=university_id)
    db.add(section)
    db.commit()
    return RedirectResponse(url="/admin/sections", status_code=303)

@router.post("/sections/delete")
def admin_sections_delete(
    section_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    section = db.query(Section).filter(Section.id == section_id).first()
    if section:
        db.delete(section)
        db.commit()
    return RedirectResponse(url="/admin/sections", status_code=303)

#---------------------------------------------

@router.get("/posts", response_class=HTMLResponse)
def admin_posts_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    error: str = Query(None)
):
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    sections = db.query(Section).all()
    universities = db.query(University).all()
    users = db.query(User).all()
    return templates.TemplateResponse("admin/posts.html", {
        "request": request,
        "user": current_user,
        "posts": posts,
        "sections": sections,
        "universities": universities,
        "users": users,
        "active": "posts",
        "error": error
    })

@router.post("/posts/delete")
def admin_posts_delete(
    post_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        db.delete(post)
        db.commit()
    return RedirectResponse(url="/admin/posts", status_code=303)

#-------------------------------------------------------------

@router.get("/reports", response_class=HTMLResponse)
def admin_reports(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    reports = crud_report.get_reports(db)
    return templates.TemplateResponse("admin/reports.html", {
        "request": request,
        "user": current_user,
        "reports": reports,
        "active": "reports"
    })
