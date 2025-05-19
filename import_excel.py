import pandas as pd
from sqlalchemy import select, update
from app.db import get_session, engine
from app.models import SQLModel, Quiz, Question, Choice

EXCEL_PATH = "data/TracNghiem.xlsx"
SHEET_NAME = "Sheet1"

# 1. Đọc & làm sạch dữ liệu
df = (
    pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
      .dropna(subset=["Câu hỏi"])
)
for col in ["A","B","C","D"]:
    df[col] = df[col].fillna("").astype(str).str.strip()

# 2. Tạo bảng nếu cần
SQLModel.metadata.create_all(engine)

with next(get_session()) as session:
    # ---- 2.1 Tạo Quiz ----
    quiz = Quiz(title="Quiz từ Excel")
    session.add(quiz)
    session.commit()
    session.refresh(quiz)

    # ---- 2.2 Bulk tạo Question ----
    q_objs = [
        Question(quiz_id=quiz.id, text=row["Câu hỏi"], correct_choice_id=0)
        for _, row in df.iterrows()
    ]
    session.bulk_save_objects(q_objs)
    session.commit()

    # Lấy lại list Question model (có .id)
    created_questions = session.exec(
        select(Question).where(Question.quiz_id == quiz.id)
    ).scalars().all()

    # ---- 2.3 Bulk tạo Choice ----
    c_objs = []
    correct_map = {}  # question_id -> đúng thứ mấy (0-based)
    for q, (_, row) in zip(created_questions, df.iterrows()):
        correct_map[q.id] = int(row["Đáp án đúng"]) - 1
        for i, col in enumerate(["A","B","C","D"]):
            text = row[col]
            if text:
                c_objs.append(Choice(question_id=q.id, text=text))
    session.bulk_save_objects(c_objs)
    session.commit()

    # Lấy lại list Choice
    created_choices = session.exec(
        select(Choice).where(Choice.question_id.in_(correct_map.keys()))
    ).scalars().all()

    # ---- 2.4 Cập nhật correct_choice_id ----
    from collections import defaultdict
    choices_by_q = defaultdict(list)
    for c in created_choices:
        choices_by_q[c.question_id].append(c)

    updates = []
    for q in created_questions:
        # sort theo ID insertion order
        choices = sorted(choices_by_q[q.id], key=lambda c: c.id)
        idx = correct_map[q.id]
        if 0 <= idx < len(choices):
            updates.append({"id": q.id, "correct_choice_id": choices[idx].id})

    if updates:
        session.execute(
            update(Question),
            updates
        )
        session.commit()

    print(f"✅ Đã import {len(created_questions)} câu hỏi từ Excel vào Quiz ID = {quiz.id}")
