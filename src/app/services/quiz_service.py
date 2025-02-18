from typing import List, Dict 
from src.app.repository.quiz_repository import QuizRepository
from src.app.models.quiz import Quiz, LanguageEnum, DifficultyLevel, quiz_question_association, QuizAttemptRecord
from src.app.models.quiz import QuestionResultRecord, Question
from src.app.schemas.schemas import QuizResponse, QuestionResponse, QuizAttempt,  QuizCreateRequest, QuizAttemptResult, QuestionResult, QuestionAttemptResult
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError
from src.app.services.question_service import QuestionService
import json
import logging
from src.app.models.quiz import QuizAttemptRecord


class QuizService:
    def __init__(self, quiz_repository: QuizRepository, db: Session):
        self.quiz_repository = quiz_repository
        self.db = db
        self.question_service = QuestionService(db)

    def add_quiz_attempt(self, quiz_attempt: QuizAttemptRecord):
        try:
            self.db.add(quiz_attempt)
            self.db.commit()
            self.db.refresh(quiz_attempt)
            return quiz_attempt
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error adding quiz attempt: {e}")
            raise HTTPException(status_code=500, detail="Error adding quiz attempt")

    def add_question_result(self, question_result: QuestionResultRecord):
        try:
            self.db.add(question_result)
            self.db.commit()
            self.db.refresh(question_result)
            return question_result
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error adding question result: {e}")
            raise HTTPException(status_code=500, detail="Error adding question result")

    def get_questions_by_quiz_id(self, quiz_id: int) -> List[QuestionResponse]:
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return [
            QuestionResponse(
                id=question.id,
                question_text=question.question_text,
                options=question.options,
                correct_option=question.correct_option,
                difficulty=question.difficulty_level
            )
            for question in quiz.questions
        ]


    

    def add(self, quiz: Quiz):
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz
    

    def get_quiz(self, quiz_id: int) -> Quiz:
        return self.db.query(Quiz).options(joinedload(Quiz.questions)).filter(Quiz.id == quiz_id).first()
    
    def attempt_quiz(self, quiz_attempt: QuizAttempt) -> List[QuestionAttemptResult]:
        results = []
        quiz_attempt_record = QuizAttemptRecord(
            student_id=quiz_attempt.student_id,
            quiz_id=quiz_attempt.quiz_id,
            total_score=0  # This will be updated later
        )
        self.add_quiz_attempt(quiz_attempt_record)

        correct_answers = 0

        for attempt in quiz_attempt.attempts:
            question = self.db.query(Question).filter(Question.id == attempt.question_id).first()
            if not question:
                raise HTTPException(status_code=404, detail=f"Question with ID {attempt.question_id} not found")

            is_correct = question.correct_option == attempt.selected_option
            if is_correct:
                correct_answers += 1

            question_result_record = QuestionResultRecord(
                attempt_id=quiz_attempt_record.id,
                question_id=question.id,
                selected_option=attempt.selected_option,
                is_correct=is_correct
            )
            self.add_question_result(question_result_record)

            results.append(QuestionAttemptResult(
                question_id=question.id,
                question_text=question.question_text,
                options=question.options,
                selected_option=attempt.selected_option,
                language=question.language.name,
                difficulty=question.difficulty_level.name
            ))

        # Update total score
        total_score = (correct_answers / len(results)) * 100
        quiz_attempt_record.total_score = total_score
        self.db.commit()

        return results

    def get_results_by_student_id(self, student_id: int) -> QuizAttemptResult:
        logging.info(f"Fetching results for student ID: {student_id}")
        attempts = self.db.query(QuizAttemptRecord).filter(QuizAttemptRecord.student_id == student_id).all()
        if not attempts:
            logging.warning(f"No results found for student ID: {student_id}")
            raise HTTPException(status_code=404, detail="Results not found for the given student ID")

        # Use the latest attempt for scoring
        latest_attempt = attempts[-1]
        previous_attempt = attempts[-2] if len(attempts) > 1 else None
        total_questions = 0
        correct_answers = 0
        results = []
        attempt_count = len(attempts)

        for question_result in latest_attempt.questions:
            question = self.db.query(Question).filter(Question.id == question_result.question_id).first()
            is_correct = question.correct_option == question_result.selected_option
            if is_correct:
                correct_answers += 1

            results.append(QuestionResult(
                question_id=question.id,
                question_text=question.question_text,
                options=question.options,
                selected_option=question_result.selected_option,
                correct_option=question.correct_option
            ))
            total_questions += 1

        total_score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        previous_score = None

        if previous_attempt:
            previous_correct_answers = sum(
                1 for question_result in previous_attempt.questions
                if self.db.query(Question).filter(Question.id == question_result.question_id).first().correct_option == question_result.selected_option
            )
            previous_total_questions = len(previous_attempt.questions)
            previous_score = (previous_correct_answers / previous_total_questions) * 100 if previous_total_questions > 0 else 0

        return QuizAttemptResult(
            student_id=student_id,
            results=results,
            total_score=total_score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            attempt_count=attempt_count,  # Include the number of attempts
            previous_score=previous_score  # Include the previous score
        )

    def add_quiz(self, quiz: Quiz):
        try:
            self.db.add(quiz)
            self.db.commit()
            self.db.refresh(quiz)
            return quiz
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error adding quiz: {e}")
            raise HTTPException(status_code=500, detail="Error adding quiz")

            
    def create_quiz_from_json(self, quiz_data: dict) -> Quiz:
        try:
            logging.info(f"Processing quiz: {quiz_data}")
            
            # Check if the language and difficulty are already enums
            if isinstance(quiz_data["language"], LanguageEnum):
                language_enum = quiz_data["language"]
            else:
                language_enum = LanguageEnum[quiz_data["language"].upper() if quiz_data["language"].upper() != "C++" else "CPP"]
            
            if isinstance(quiz_data["difficulty"], DifficultyLevel):
                difficulty_enum = quiz_data["difficulty"]
            else:
                difficulty_enum = DifficultyLevel[quiz_data["difficulty"].upper()]
            
            quiz = Quiz(
                title=quiz_data["title"],
                description=quiz_data["description"],
                language=language_enum.name,  # Convert to string
                difficulty=difficulty_enum.name  # Convert to string
            )

            for question_data in quiz_data.get("questions", []):
                logging.info(f"Processing question: {question_data}")
                
                # Check if the language and difficulty are already enums
                if isinstance(question_data.get("language", quiz_data["language"]), LanguageEnum):
                    question_language_enum = question_data["language"]
                else:
                    question_language_enum = LanguageEnum[question_data.get("language", quiz_data["language"]).upper() if question_data.get("language", quiz_data["language"]).upper() != "C++" else "CPP"]
                
                if isinstance(question_data["difficulty"], DifficultyLevel):
                    question_difficulty_enum = question_data["difficulty"]
                else:
                    question_difficulty_enum = DifficultyLevel[question_data["difficulty"].upper()]
                
                question = Question(
                    question_text=question_data["question_text"],
                    options=question_data["options"],
                    correct_option=question_data["correct_option"],
                    language=question_language_enum.name,  # Convert to string
                    difficulty_level=question_difficulty_enum.name  # Convert to string
                )
                quiz.questions.append(question)

            return quiz
        except KeyError as e:
            logging.error(f"KeyError: {e}")
            raise HTTPException(status_code=400, detail=f"Error processing file: {e}")

    def add(self, quiz: Quiz):
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def delete_quiz(self, quiz_id: int):
        quiz = self.get_quiz(quiz_id)
        self.db.delete(quiz)
        self.db.commit()

    def update_quiz(self, quiz_id: int, quiz_update: QuizCreateRequest) -> Quiz:
        quiz = self.get_quiz(quiz_id)
        for key, value in quiz_update.dict().items():
            setattr(quiz, key, value)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz