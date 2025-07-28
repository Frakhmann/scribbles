import app.db.base

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.routers import admin
from app.admin_login import router as admin_login_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Scribbles Admin Panel",
    docs_url="/admin/docs",
    openapi_url="/admin/openapi.json",
    redoc_url=None,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.add_middleware(SessionMiddleware, secret_key="super-secret-key")
app.include_router(admin_login_router)
app.include_router(admin.router)
