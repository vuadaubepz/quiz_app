from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    registered_at: datetime = Field(default_factory=datetime.utcnow)

class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    questions: List["Question"] = Relationship(back_populates="quiz")

class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quiz.id")
    text: str
    correct_choice_id: int
    quiz: Optional[Quiz] = Relationship(back_populates="questions")
    choices: List["Choice"] = Relationship(back_populates="question")

class Choice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id")
    text: str
    question: Optional[Question] = Relationship(back_populates="choices")
