from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session
from datetime import datetime

from app.db import get_session
from app.models import Quiz, Question, Choice

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/topics", response_class=templates.TemplateResponse)
def list_topics(request: Request, session: Session = Depends(get_session)):
    quizzes = session.exec(select(Quiz)).all()
    return templates.TemplateResponse("topics.html", {
        "request": request,
        "quizzes": quizzes,
        "year": datetime.utcnow().year
    })

@router.get("/quiz/{quiz_id}", response_class=templates.TemplateResponse)
def start_quiz(request: Request, quiz_id: int, session: Session = Depends(get_session)):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    items = []
    questions = session.exec(select(Question).where(Question.quiz_id == quiz_id)).all()
    for q in questions:
        choices = session.exec(select(Choice).where(Choice.question_id == q.id)).all()
        items.append({"q": q, "choices": choices})

    return templates.TemplateResponse("quiz.html", {
        "request": request,
        "quiz": quiz,
        "qs_data": items,
        "duration_min": 45
    })

@router.post("/quiz/{quiz_id}/submit", response_class=templates.TemplateResponse)
async def submit_quiz(request: Request, quiz_id: int, session: Session = Depends(get_session)):
    form = await request.form()
    correct = total = 0
    for key, val in form.multi_items():
        if key.startswith("q"):
            total += 1
            choice = session.get(Choice, int(val))
            if choice and choice.is_correct:
                correct += 1
    return templates.TemplateResponse("result.html", {
        "request": request,
        "score": correct,
        "total": total
    })
