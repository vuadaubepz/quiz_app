from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, select, Session
from datetime import datetime

from app.db import engine, get_session
from app.models import Quiz
from app.routes.auth import router as auth_router
from app.routes.quiz import router as quiz_router

app = FastAPI()

# Mount static files (/static/...)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Auth + Quiz routers
app.include_router(auth_router)
app.include_router(quiz_router)

# Redirect root to /topics
@app.get("/", response_class=templates.TemplateResponse)
def root(request: Request):
    return templates.TemplateResponse("redirect.html", {"request": request, "url": "/topics"})

# Test DB
@app.get("/test-db")
def test_db(session: Session = Depends(get_session)):
    results = session.exec(select(Quiz)).all()
    return {"quizzes": [q.title for q in results]}
