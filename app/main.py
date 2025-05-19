from fastapi import FastAPI, Depends, Request
# from fastapi.staticfiles import StaticFiles   ← Bỏ import nếu không dùng
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, select, Session
from app.db import engine, get_session
from app.models import Quiz
from app.routes.auth import router as auth_router
from app.routes.quiz import router as quiz_router

app = FastAPI()

# Không mount static nếu không có thư mục
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(auth_router)
app.include_router(quiz_router)

@app.get("/", response_class=templates.TemplateResponse)
def home(request: Request, session: Session = Depends(get_session)):
    quizzes = session.exec(select(Quiz)).all()
    return templates.TemplateResponse("topics.html", {
        "request": request,
        "quizzes": quizzes
    })

@app.get("/test-db")
def test_db(session: Session = Depends(get_session)):
    results = session.exec(select(Quiz)).all()
    return {"quizzes": [q.title for q in results]}
