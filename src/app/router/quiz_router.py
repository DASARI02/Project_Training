from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from src.app.schemas.schemas import QuizAttempt, QuizAttemptResult, QuizResponse, QuestionAttemptResult, QuizCreateRequest, QuizAttemptResult
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
    except json.JSONDecodeError as e:
        logging.error(f"JSONDecodeError: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")
    except KeyError as e:
        logging.error(f"KeyError: {e}")
        raise HTTPException(status_code=400, detail=f"Missing key in JSON data: {e}")
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing file: {e}")


@quiz_router.get("/quizzes/{quiz_id}")
def get_quiz_by_id(quiz_id: int, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    quiz = quiz_service.get_questions_by_quiz_id(quiz_id)
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

@quiz_router.post("/create-quiz")
def create_quiz(quiz_request: QuizCreateRequest, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    quiz = quiz_service.create_quiz_from_json(quiz_request.dict())
    quiz_service.add_quiz(quiz)
    return quiz