from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlmodel import select, Session
from datetime import datetime

from app.db import get_session
from app.models import Quiz, Question, Choice

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/topics")
async def list_topics(request: Request, session: Session = Depends(get_session)):
    quizzes = session.exec(select(Quiz)).all()
    return templates.TemplateResponse(
        "topics.html",
        {
            "request": request,
            "quizzes": quizzes,
            "year": datetime.utcnow().year,
        },
    )


@router.get("/quiz/{quiz_id}")
async def start_quiz(
    request: Request, quiz_id: int, session: Session = Depends(get_session)
):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Lấy câu hỏi & lựa chọn
    questions = session.exec(
        select(Question).where(Question.quiz_id == quiz_id)
    ).all()

    items = []
    for q in questions:
        choices = session.exec(
            select(Choice).where(Choice.question_id == q.id)
        ).all()
        items.append({"q": q, "choices": choices})

    return templates.TemplateResponse(
        "quiz.html",
        {
            "request": request,
            "quiz": quiz,
            "qs_data": items,
            "duration": 45,  # phút
        },
    )


@router.post("/quiz/{quiz_id}/submit")
async def submit_quiz(
    request: Request, quiz_id: int, session: Session = Depends(get_session)
):
    # Xác nhận quiz tồn tại
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Lấy danh sách câu hỏi
    questions = session.exec(
        select(Question).where(Question.quiz_id == quiz_id)
    ).all()

    form = await request.form()
    score = 0
    total = len(questions)

    for q in questions:
        # input name là "q<id>"
        sel = form.get(f"q{q.id}")
        if not sel:
            continue
        try:
            selected_id = int(sel)
        except (ValueError, TypeError):
            continue

        # so sánh trực tiếp với correct_choice_id
        if selected_id == q.correct_choice_id:
            score += 1

    return templates.TemplateResponse(
        "leaderboard.html",
        {
            "request": request,
            "score": score,
            "total": total,
            "year": datetime.utcnow().year,
        },
    )
