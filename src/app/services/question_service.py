from src.app.schemas.schemas import QuestionResponse
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from src.app.models.quiz import DifficultyLevel, LanguageEnum, Question
import logging
from src.app.repository.question_repository import QuestionRepository


class QuestionService:
    def __init__(self, db: Session):
        self.db = db
        self.question_repository = QuestionRepository(db)

    def create_question_from_json(self, question_data: dict) -> Question:
            try:
                logging.info(f"Processing question: {question_data}")
                language_mapping = {
                    "PYTHON": LanguageEnum.PYTHON,
                    "C++": LanguageEnum.CPP,
                    "JAVA": LanguageEnum.JAVA
                }
                language_enum = language_mapping[question_data["language"].upper()]
                difficulty_enum = DifficultyLevel[question_data["difficulty"].upper()]

                question = Question(
                    question_text=question_data["question_text"],
                    options=question_data["options"],
                    correct_option=question_data["correct_option"],
                    language=language_enum,
                    difficulty_level=difficulty_enum
                )

                return question
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                raise HTTPException(status_code=400, detail=f"Error processing file: {e}")

    def add(self, question: Question):
                self.db.add(question)
                self.db.commit()
                self.db.refresh(question)
                return question

    






    def get_question_by_text(self, question_text: str, language: str) -> Question:
        try:
            language_mapping = {
                "PYTHON": LanguageEnum.PYTHON,
                "C++": LanguageEnum.CPP,
                "JAVA": LanguageEnum.JAVA
            }
            language_enum = language_mapping[language.upper()]
            question = self.db.query(Question).filter(
                Question.question_text == question_text,
                Question.language == language_enum
            ).first()
            return question
        except Exception as e:
            logging.error(f"Error getting question by text: {e}")
            raise HTTPException(status_code=500, detail="Error getting question by text")
        
    def get_questions_by_language_and_difficulty(self, language: str, difficulty: str) -> List[QuestionResponse]:
        try:
            language_mapping = {
                "PYTHON": LanguageEnum.PYTHON,
                "C++": LanguageEnum.CPP,
                "JAVA": LanguageEnum.JAVA
            }
            language_enum = language_mapping[language.upper()]
            difficulty_enum = DifficultyLevel[difficulty.upper()]

            questions = self.db.query(Question).filter(
                Question.language == language_enum,
                Question.difficulty_level == difficulty_enum
            ).all()

            return [
                QuestionResponse(
                    id=question.id,
                    question_text=question.question_text,
                    options=question.options,
                    correct_option=question.correct_option,
                    difficulty=question.difficulty_level
                )
                for question in questions
            ]
        except KeyError as e:
            logging.error(f"KeyError: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid language or difficulty: {e}")
        except Exception as e:
            logging.error(f"Error getting questions: {e}")
            raise HTTPException(status_code=500, detail="Error getting questions")
        
  