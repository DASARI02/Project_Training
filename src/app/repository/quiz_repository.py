from fastapi import HTTPException  
from sqlalchemy.orm import Session, relationship
from src.app.models.quiz import Quiz, quiz_question_association, QuizAttemptRecord
from typing import List
from src.app.models.quiz import Question, QuestionResultRecord

class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_quiz_by_id(self, quiz_id: int) -> Quiz:
        return self.db.query(Quiz).filter(Quiz.id == quiz_id).first()

    # def get_quiz_attempts_by_student_id(self, student_id: int) -> List[QuizAttemptRecord]:
    #     return self.db.query(QuizAttemptRecord).filter(QuizAttemptRecord.student_id == student_id).all()

    # def get_student_results(self, student_id: int):
    #     pass

    # def delete_quiz(self, quiz_id: int):
    #     quiz = self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
    #     if quiz:
    #         self.db.delete(quiz)
    #         self.db.commit()