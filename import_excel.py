# import_excel.py
import glob
import pandas as pd
from sqlmodel import Session
from app.db import engine
from app.models import Quiz, Question, Choice

def import_all_from_excels():
    # Giả sử bạn để các file ở thư mục data/
    paths = glob.glob("data/TracNghiem*.xlsx")
    with Session(engine) as session:
        for path in paths:
            # Đọc toàn bộ sheet đầu tiên
            df = pd.read_excel(path)
            if df.empty:
                continue

            # Lấy tên chủ đề (giả định tất cả dòng trong file này đều cùng 1 chủ đề)
            topic = df["Chủ đề"].iloc[0].strip()
            print(f"Import Quiz: {topic}")

            # Tạo Quiz mới
            quiz = Quiz(title=topic)
            session.add(quiz)
            session.commit()
            session.refresh(quiz)

            # Cho mỗi dòng là một câu hỏi
            for _, row in df.iterrows():
                q_text = str(row["Câu hỏi"]).strip()
                question = Question(text=q_text, quiz_id=quiz.id)
                session.add(question)
                session.commit()
                session.refresh(question)

                # Tạo 4 đáp án A, B, C, D
                correct = str(row["Đáp án đúng"]).strip().upper()
                for opt in ["A", "B", "C", "D"]:
                    choice_text = str(row[opt]).strip()
                    is_corr = (opt == correct)
                    choice = Choice(
                        text=choice_text,
                        question_id=question.id,
                        is_correct=is_corr
                    )
                    session.add(choice)
                session.commit()
    print("Hoàn thành import tất cả Excel files.")

if __name__ == "__main__":
    import_all_from_excels()
