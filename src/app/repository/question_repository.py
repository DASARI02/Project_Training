from fastapi import HTTPException  
from sqlalchemy.orm import Session
from typing import List
from src.app.models.quiz import Question, QuestionResultRecord, LanguageEnum, DifficultyLevel
import logging
from sqlalchemy.sql.expression import func

class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db
        logging.info(f"Database session initialized: {self.db}")

    def get_by_id(self, question_id: int) -> Question:
        logging.info(f"Fetching question with ID: {question_id}")
        return self.db.query(Question).filter(Question.id == question_id).first()

    def add(self, question: Question):
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question
    
    # def get_random_questions(self, language: str, difficulty: str, page: int, page_size: int) -> List[Question]:
    #     language_enum = LanguageEnum[language.upper()]
    #     difficulty_enum = DifficultyLevel[difficulty.upper()]
    #     offset = (page - 1) * page_size
    #     return self.db.query(Question).filter(
    #         Question.language == language_enum,
    #         Question.difficulty_level == difficulty_enum
    #     ).order_by(func.random()).offset(offset).limit(page_size).all()

    # def get_question_results_by_attempt_id(self, attempt_id: int) -> List[QuestionResultRecord]:
    #     return self.db.query(QuestionResultRecord).filter(QuestionResultRecord.attempt_id == attempt_id).all()

    # def delete_question(self, question_id: int):
    #     question = self.db.query(Question).filter(Question.id == question_id).first()
    #     if question:
    #         self.db.delete(question)
    #         self.db.commit()