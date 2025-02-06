from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from src.app.schemas.schemas import QuizAttempt, QuizAttemptResult, QuizResponse, QuizResultsResponse, QuestionResponse, QuestionAttemptResult
from src.app.services.quiz_service import QuizService
from src.app.repository.quiz_repository import QuizRepository
from sqlalchemy.orm import Session
from src.app.config.database import get_db
from typing import List 
import json 
import logging 

quiz_router = APIRouter()



@quiz_router.post("/upload-quizzes")
async def upload_quizzes(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        data = json.loads(contents.decode('utf-8'))
        
        quiz_service = QuizService(QuizRepository(db), db)
        
        for quiz_data in data["quizzes"]:
            logging.info(f"Processing quiz: {quiz_data}")
            quiz = quiz_service.create_quiz_from_json(quiz_data)
            quiz_service.add(quiz)
        
        return {"message": "Quizzes uploaded successfully"}
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing file: {e}")


@quiz_router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
def get_quiz_by_id(quiz_id: int, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    quiz = quiz_service.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@quiz_router.post("/quizzes/attempt", response_model=List[QuestionAttemptResult])
def attempt_quiz(quiz_attempt: QuizAttempt, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    results = quiz_service.attempt_quiz(quiz_attempt)
    return results

@quiz_router.get("/quizzes/results/{student_id}", response_model=QuizAttemptResult)
def get_results_by_student_id(student_id: int, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    results = quiz_service.get_results_by_student_id(student_id)
    return results

# @quiz_router.post("/attempt-quiz/{quiz_id}", response_model=QuizAttemptResult)
# def attempt_quiz(quiz_id: int, quiz_attempt: QuizAttempt, db: Session = Depends(get_db)):
#     quiz_service = QuizService(QuizRepository(db))
#     result = quiz_service.attempt_quiz(quiz_id, quiz_attempt, db)
#     return result

# @quiz_router.get("/results/{student_id}", response_model=List[QuizResultsResponse])
# def get_results_by_student_id(student_id: int, db: Session = Depends(get_db)):
#     quiz_service = QuizService(QuizRepository(db))
#     results = quiz_service.get_results_by_student_id(student_id)
#     return results

#@quiz_router.get("/questions", response_model=List[QuestionResponse])
# def get_questions_by_language_and_difficulty(language: str, difficulty: str, db: Session = Depends(get_db)):
#     quiz_service = QuizService(QuizRepository(db), db)
#     questions = quiz_service.get_questions_by_language_and_difficulty(language, difficulty)
#     if not questions:
#         raise HTTPException(status_code=404, detail="Questions not found for the given language and difficulty")
#     return questions

#@quiz_router.get("/quiz/{quiz_id}/questions", response_model=List[QuestionResponse])
# def get_questions_by_quiz_id(quiz_id: int, db: Session = Depends(get_db)):
#     quiz_service = QuizService(QuizRepository(db), db)
#     questions = quiz_service.get_questions_by_quiz_id(quiz_id)
#     if not questions:
#         raise HTTPException(status_code=404, detail="Questions not found for the given quiz ID")
#     return questions


# @quiz_router.get("/{quiz_id}", response_model=QuizResponse)
# def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
#     quiz_service = QuizService(QuizRepository(db), db)
#     quiz = quiz_service.get_quiz_by_id(quiz_id)
#     return quiz

# @quiz_router.post("/quiz/{quiz_id}/add-questions")
# def add_questions_to_quiz(quiz_id: int, question_ids: List[int], db: Session = Depends(get_db)):
#     quiz_service = QuizService(QuizRepository(db), db)
#     return quiz_service.add_questions_to_quiz(quiz_id, question_ids)