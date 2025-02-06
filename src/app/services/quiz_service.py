from typing import List, Dict 
from src.app.repository.quiz_repository import QuizRepository
from src.app.models.quiz import Quiz, LanguageEnum, DifficultyLevel, quiz_question_association, QuizAttemptRecord
from src.app.models.quiz import QuestionResultRecord, Question
from src.app.schemas.schemas import QuizResponse, QuestionResponse, QuizAttempt,  ResultSchema, QuizResultsResponse, QuizAttemptResult, QuestionResult, QuestionAttemptResult
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError
from src.app.services.question_service import QuestionService
import json
import logging



class QuizService:
    def __init__(self, quiz_repository: QuizRepository, db: Session):
        self.quiz_repository = quiz_repository
        self.db = db
        self.question_service = QuestionService(db)

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


    def create_quiz_from_json(self, quiz_data: dict) -> Quiz:
        try:
            logging.info(f"Processing quiz: {quiz_data}")
            language_mapping = {
                "PYTHON": LanguageEnum.PYTHON,
                "C++": LanguageEnum.CPP,
                "JAVA": LanguageEnum.JAVA
            }
            language_enum = language_mapping[quiz_data["language"].upper()]
            difficulty_enum = DifficultyLevel[quiz_data["difficulty"].upper()]

            quiz = Quiz(
                title=quiz_data["title"],
                description=quiz_data["description"],
                language=language_enum,
                difficulty=difficulty_enum
            )

            for question_data in quiz_data.get("questions", []):
                question = Question(
                    question_text=question_data["question_text"],
                    options=question_data["options"],
                    correct_option=question_data["correct_option"],
                    language=language_enum,
                    difficulty_level=difficulty_enum
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
    

    def get_quiz(self, quiz_id: int) -> Quiz:
        return self.db.query(Quiz).options(joinedload(Quiz.questions)).filter(Quiz.id == quiz_id).first()
    
    def attempt_quiz(self, quiz_attempt: QuizAttempt) -> List[QuestionAttemptResult]:
        results = []

        for attempt in quiz_attempt.attempts:
            question = self.db.query(Question).filter(Question.id == attempt.question_id).first()
            if not question:
                raise HTTPException(status_code=404, detail=f"Question with ID {attempt.question_id} not found")

            results.append(QuestionAttemptResult(
                question_id=question.id,
                question_text=question.question_text,
                options=question.options,
                selected_option=attempt.selected_option,
                language=question.language.name,
                difficulty=question.difficulty_level.name
            ))

        return results

    def get_results_by_student_id(self, student_id: int) -> QuizAttemptResult:
        # Fetch results from the database based on student_id
        # This is a placeholder implementation and should be replaced with actual database queries
        attempts = self.db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()
        if not attempts:
            raise HTTPException(status_code=404, detail="Results not found for the given student ID")

        total_questions = len(attempts)
        correct_answers = 0
        results = []

        for attempt in attempts:
            question = self.db.query(Question).filter(Question.id == attempt.question_id).first()
            is_correct = question.correct_option == attempt.selected_option
            if is_correct:
                correct_answers += 1

            results.append(QuestionResult(
                question_id=question.id,
                question_text=question.question_text,
                options=question.options,
                selected_option=attempt.selected_option,
                correct_option=question.correct_option
            ))

        total_score = (correct_answers / total_questions) * 100

        return QuizAttemptResult(
            student_id=student_id,
            results=results,
            total_score=total_score,
            total_questions=total_questions,
            correct_answers=correct_answers
        )



    # def add_questions_to_quiz(self, quiz_id: int, question_ids: List[int]):
    #     quiz = self.quiz_repository.get_quiz_by_id(quiz_id)
    #     if not quiz:
    #         raise HTTPException(status_code=404, detail="Quiz not found")

    #     questions = self.db.query(Question).filter(Question.id.in_(question_ids)).all()
    #     if not questions:
    #         raise HTTPException(status_code=404, detail="Questions not found")

    #     quiz.questions.extend(questions)
    #     self.db.commit()
    #     return quiz
    
    # def get_serialized_quiz(self, quiz_id: int) -> Dict:
    #     quiz = self.get_quiz(quiz_id)
    #     if quiz is None:
    #         raise HTTPException(status_code=404, detail="Quiz not found")
    #     return serialize_quiz(quiz)

    # def attempt_quiz(self, quiz_id: int, quiz_attempt: QuizAttempt) -> QuizAttemptResult:
    #     quiz = self.get_quiz(quiz_id)
    #     if not quiz:
    #         raise HTTPException(status_code=404, detail="Quiz not found")

    #     previous_attempts = self.db.query(QuizAttemptRecord).filter(
    #         QuizAttemptRecord.student_id == quiz_attempt.student_id,
    #         QuizAttemptRecord.quiz_id == quiz_id
    #     ).count()
    #     attempt_number = previous_attempts + 1

    #     results = []
    #     total_score = 0
    #     for attempt in quiz_attempt.attempts:
    #         question = next((q for q in quiz.questions if q.id == attempt.question_id), None)
    #         if not question:
    #             raise HTTPException(status_code=404, detail=f"Question with ID {attempt.question_id} not found in quiz")

    #         if attempt.selected_option not in question.options:
    #             raise HTTPException(status_code=400, detail=f"Invalid option selected for question ID {attempt.question_id}")

    #         score = calculate_combined_score(question, attempt.selected_option)
    #         total_score += score

    #         result = QuestionResult(
    #             question_id=question.id,
    #             question_text=question.question_text,
    #             options=question.options,
    #             selected_option=attempt.selected_option
    #         )
    #         results.append(result)

    #     try:
    #         quiz_attempt_record = QuizAttemptRecord(
    #             student_id=quiz_attempt.student_id,
    #             quiz_id=quiz.id,
    #             total_score=total_score
    #         )
    #         self.db.add(quiz_attempt_record)
    #         self.db.commit()
    #         self.db.refresh(quiz_attempt_record)

    #         for result in results:
    #             question_result_record = QuestionResultRecord(
    #                 attempt_id=quiz_attempt_record.id,
    #                 question_id=result.question_id,
    #                 selected_option=result.selected_option,
    #                 is_correct=result.is_correct
    #             )
    #             self.db.add(question_result_record)
    #         self.db.commit()

    #     except IntegrityError as e:
    #         self.db.rollback()
    #         raise HTTPException(status_code=400, detail="Student ID does not exist in the users table.")

    #     return QuizAttemptResult(
    #         student_id=quiz_attempt.student_id,
    #         quiz_id=quiz.id,
    #         title=quiz.title,
    #         language=quiz.language.value,
    #         description=quiz.description,
    #         results=results,
    #         attempt_number=attempt_number
    #     )

    def get_quiz_by_id(self, quiz_id: int) -> Dict:
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        return {
            "id": quiz.id,
            "title": quiz.title,
            "language": quiz.language.value,
            "description": quiz.description,
            "questions": [
                {
                    "id": question.id,
                    "text": question.question_text,
                    "options": question.options
                }
                for question in quiz.questions
            ]
        }

    # def get_quiz_results(self, student_id: int) -> List[QuizResponse]:
    #     results = self.quiz_repository.get_student_results(student_id)
    #     return [QuizResponse.model_validate(result) for result in results]

    # def get_random_questions(self, language: LanguageEnum) -> List[Dict]:
    #     questions = self.db.query(Question).filter(Question.language == language).order_by(func.random()).limit(10).all()
    #     return [{"id": q.id, "question_text": q.question_text, "options": q.options} for q in questions]

    # def delete_quiz(self, quiz_id: int):
    #     self.quiz_repository.delete_quiz(quiz_id)

    # def get_latest_results_by_student_id(self, student_id: int) -> List[QuizResultsResponse]:
    #     quiz_attempts = self.quiz_repository.get_latest_quiz_attempts_by_student_id(student_id)
    #     results = []
    #     for attempt in quiz_attempts:
    #         question_results = self.quiz_repository.get_question_results_by_attempt_id(attempt.id)
    #         correct_answers = sum(1 for result in question_results if result.is_correct)
    #         total_questions = len(question_results)
    #         results.append(QuizResultsResponse(
    #             student_id=attempt.student_id,
    #             total_score=correct_answers,  # Ensure total_score is the number of correct answers
    #             total_questions=total_questions,
    #             correct_answers=correct_answers,
    #             results=[
    #                 ResultSchema(
    #                     question_text=result.question.question_text,
    #                     correct_option=result.question.correct_option,
    #                     student_selected=result.selected_option,
    #                     is_correct=result.is_correct
    #                 )
    #                 for result in question_results
    #             ]
    #         ))
    #     return results

    # def get_results_by_student_id(self, student_id: int) -> List[QuizResultsResponse]:
    #     quiz_attempts = self.quiz_repository.get_quiz_attempts_by_student_id(student_id)
    #     results = []
    #     for attempt in quiz_attempts:
    #         question_results = self.quiz_repository.get_question_results_by_attempt_id(attempt.id)
    #         correct_answers = sum(1 for result in question_results if result.is_correct)
    #         total_questions = len(question_results)
    #         results.append(QuizResultsResponse(
    #             student_id=attempt.student_id,
    #             total_score=correct_answers,  # Ensure total_score is the number of correct answers
    #             total_questions=total_questions,
    #             correct_answers=correct_answers,
    #             results=[
    #                 ResultSchema(
    #                     question_text=result.question.question_text,
    #                     correct_option=result.question.correct_option,
    #                     student_selected=result.selected_option,
    #                     is_correct=result.is_correct
    #                 )
    #                 for result in question_results
    #             ]
    #         ))
    #     return results

# def calculate_combined_score(question, selected_option):
#     score = 0
#     if selected_option == question.correct_option:
#         if question.difficulty_level == DifficultyLevel.EASY:
#             score += 1
#         elif question.difficulty_level == DifficultyLevel.MEDIUM:
#             score += 2
#         elif question.difficulty_level == DifficultyLevel.HARD:
#             score += 3
#     return max(score, 0)  

# def get_questions_for_quiz(quiz: Quiz) -> List[Dict]:
#     return [
#         {
#             "question_id": question.id,
#             "text": question.question_text,
#             "options": question.options
#         }
#         for question in quiz.questions
#     ]
# def serialize_quiz(quiz: Quiz) -> Dict:
#     return {
#         "quiz_id": quiz.id,
#         "title": quiz.title,
#         "language": quiz.language.value,
#         "description": quiz.description,
#         "questions": get_questions_for_quiz(quiz)
#     }