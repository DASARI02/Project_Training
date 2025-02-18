from src.app.schemas.schemas import QuestionResponse, QuestionCreate
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
        self.language_mapping = {
            "PYTHON": LanguageEnum.PYTHON,
            "C++": LanguageEnum.CPP,
            "JAVA": LanguageEnum.JAVA,
            "JAVASCRIPT": LanguageEnum.JAVASCRIPT
        }

    def create_question_from_json(self, question_data: dict) -> Question:
            try:
                logging.info(f"Processing question: {question_data}")
                language_mapping = {
                    "PYTHON": LanguageEnum.PYTHON,
                    "C++": LanguageEnum.CPP,
                    "JAVA": LanguageEnum.JAVA,
                    "JAVASCRIPT": LanguageEnum.JAVASCRIPT
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
            logging.info(f"Fetching question with text: {question_text} and language: {language}")
            language_enum = self.language_mapping[language.upper()]
            question = self.db.query(Question).filter(
                Question.question_text == question_text,
                Question.language == language_enum
            ).first()
            logging.info(f"Found question: {question}")
            return question
        except KeyError as e:
            logging.error(f"KeyError: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid language: {e}")
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
        
    def get_question_by_id(self, question_id: int) -> Question:
        return self.db.query(Question).filter(Question.id == question_id).first()

    def delete_question(self, question_id: int):
        question = self.get_question_by_id(question_id)
        self.db.delete(question)
        self.db.commit()

    def update_question(self, question_id: int, question_update: QuestionCreate) -> Question:
        question = self.get_question_by_id(question_id)
        for key, value in question_update.dict().items():
            setattr(question, key, value)
        self.db.commit()
        self.db.refresh(question)
        return question