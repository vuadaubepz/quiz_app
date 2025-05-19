# app/routes/auth.py
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db import get_session
from sqlmodel import Session, select
from app.models import User
from app.auth import hash_password, verify_password, create_access_token
from starlette.status import HTTP_302_FOUND

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    exists = session.exec(select(User).where(User.email == email)).first()
    if exists:
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "Email đã tồn tại."
        })
    user = User(email=email, hashed_password=hash_password(password))
    session.add(user); session.commit()
    response = RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    return response

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request, "error": "Email hoặc mật khẩu sai."
        })
    token = create_access_token(subject=str(user.id))
    response = RedirectResponse(url="/topics", status_code=HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response
