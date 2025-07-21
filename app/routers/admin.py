from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from fastapi.templating import Jinja2Templates

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
