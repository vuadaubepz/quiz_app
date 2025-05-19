from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.db import get_session
from app.models import Quiz, Question, Choice
from datetime import datetime
import random

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Lưu session quiz tạm (sẽ chuyển Redis/DB khi mở rộng)
SESSIONS: dict[int, dict] = {}

@router.get("/topics", response_class=HTMLResponse)
def list_topics(request: Request, session: Session = Depends(get_session)):
    quizzes = session.exec(select(Quiz)).all()
    return templates.TemplateResponse("topics.html", {
        "request": request,
        "quizzes": quizzes,
    })

@router.get("/quiz/{quiz_id}", response_class=HTMLResponse)
def start_quiz(
    request: Request,
    quiz_id: int,
    session: Session = Depends(get_session)
):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz không tồn tại")

    questions = session.exec(
        select(Question).where(Question.quiz_id == quiz_id)
    ).all()
    sampled = random.sample(questions, min(len(questions), 100))

    SESSIONS[quiz_id] = {
        "start_time": datetime.utcnow(),
        "questions": [q.id for q in sampled],
        "answers": {}
    }

    qs_data = []
    for q in sampled:
        choices = session.exec(
            select(Choice).where(Choice.question_id == q.id)
        ).all()
        qs_data.append({"question": q, "choices": choices})

    return templates.TemplateResponse("quiz.html", {
        "request": request,
        "quiz": quiz,
        "qs_data": qs_data,
        "duration_min": 45
    })

@router.post("/quiz/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    us = SESSIONS.get(quiz_id)
    if not us:
        raise HTTPException(status_code=400, detail="Session không tồn tại")

    form_data = await request.form()
    correct = 0
    for qid in us["questions"]:
        selected = int(form_data.get(f"q{qid}", 0))
        question = session.get(Question, qid)
        if selected == question.correct_choice_id:
            correct += 1

    return RedirectResponse(
        url=f"/leaderboard/{quiz_id}?score={correct}",
        status_code=302
    )

@router.get("/leaderboard/{quiz_id}", response_class=HTMLResponse)
def leaderboard(
    request: Request,
    quiz_id: int,
    score: int = 0,
    session: Session = Depends(get_session)
):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz không tồn tại")

    return templates.TemplateResponse("leaderboard.html", {
        "request": request,
        "quiz": quiz,
        "score": score,
    })
