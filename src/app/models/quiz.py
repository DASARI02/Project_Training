#src/models/quiz_model.py
from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, JSON, Table, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from src.app.config.database import Base
from sqlalchemy.sql import func
import enum

class LanguageEnum(enum.Enum):
    PYTHON = "PYTHON"
    JAVA = "JAVA"
    CPP = "C++"
    JAVASCRIPT = "JAVASCRIPT"

class DifficultyLevel(enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

quiz_question_association = Table(
    'quiz_question_association',
    Base.metadata,
    Column('quiz_id', Integer, ForeignKey('quizzes.id'), primary_key=True),
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True)
)

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    language = Column(SQLAEnum(LanguageEnum, name="language_enum"), nullable=False)
    difficulty = Column(SQLAEnum(DifficultyLevel, name="difficulty_enum"), nullable=False)
    questions = relationship("Question", secondary=quiz_question_association, back_populates="quizzes")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_text = Column(String, nullable=False)
    options = Column(JSON, nullable=False)
    language = Column(SQLAEnum(LanguageEnum, name="language_enum"), nullable=False)
    correct_option = Column(String, nullable=False)
    difficulty_level = Column(SQLAEnum(DifficultyLevel, name="difficulty_enum"), nullable=False)
    quizzes = relationship("Quiz", secondary=quiz_question_association, back_populates="questions")

class QuizAttemptRecord(Base):
    __tablename__ = 'quiz_attempts'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    total_score = Column(Integer, nullable=False)
    attempt_date = Column(TIMESTAMP, default=func.now())
    questions = relationship("QuestionResultRecord", back_populates="quiz_attempt")

class QuestionResultRecord(Base):
    __tablename__ = 'question_results'

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    selected_option = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    question = relationship("Question")
    quiz_attempt = relationship("QuizAttemptRecord", back_populates="questions")