# app/db.py
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

DATABASE_URL = "sqlite:///./quiz.db"   # lúc dev dùng SQLite, production có thể đổi PostgreSQL

engine = create_engine(
    DATABASE_URL, 
    echo=True, 
    connect_args={"check_same_thread": False}  # SQLite cần
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
