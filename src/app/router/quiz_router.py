from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from src.app.config.database import get_db
from src.app.schemas.schemas import QuizAttempt, QuizAttemptResult, QuizResponse, QuestionAttemptResult, QuizCreateRequest
from src.app.services.quiz_service import QuizService
from src.app.repository.quiz_repository import QuizRepository
from src.app.auth.auth import get_current_admin_user, get_current_student_user
from typing import List
import json
import logging

quiz_router = APIRouter()

@quiz_router.post("/upload-quizzes", dependencies=[Depends(get_current_admin_user)])
async def upload_quizzes(file: UploadFile = File(), db: Session = Depends(get_db)):
    
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

@quiz_router.get("/quizzes/{quiz_id}", dependencies=[Depends(get_current_student_user)])
def get_quiz_by_id(quiz_id: int, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    quiz = quiz_service.get_questions_by_quiz_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@quiz_router.post("/quizzes/attempt", response_model=List[QuestionAttemptResult], dependencies=[Depends(get_current_student_user)])
def attempt_quiz(quiz_attempt: QuizAttempt, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    results = quiz_service.attempt_quiz(quiz_attempt)
    return results

@quiz_router.get("/quizzes/results/{student_id}", response_model=QuizAttemptResult, dependencies=[Depends(get_current_student_user)])
def get_results_by_student_id(student_id: int, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    results = quiz_service.get_results_by_student_id(student_id)
    return results

@quiz_router.post("/create-quiz", dependencies=[Depends(get_current_admin_user)])
def create_quiz(quiz_request: QuizCreateRequest, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    quiz = quiz_service.create_quiz_from_json(quiz_request.dict())
    quiz_service.add_quiz(quiz)
    return quiz

@quiz_router.delete("/quizzes/{quiz_id}", dependencies=[Depends(get_current_admin_user)])
def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    quiz = quiz_service.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    quiz_service.delete_quiz(quiz_id)
    return {"message": "Quiz deleted successfully"}

@quiz_router.patch("/quizzes/{quiz_id}", dependencies=[Depends(get_current_admin_user)])
def update_quiz(quiz_id: int, quiz_update: QuizCreateRequest, db: Session = Depends(get_db)):
    quiz_service = QuizService(QuizRepository(db), db)
    quiz = quiz_service.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    updated_quiz = quiz_service.update_quiz(quiz_id, quiz_update)
    return updated_quiz