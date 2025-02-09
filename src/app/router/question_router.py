from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from src.app.config.database import get_db
from src.app.services.question_service import QuestionService
from src.app.services.quiz_service import QuizService
from src.app.schemas.schemas import QuestionResponse, QuizAttempt, QuizAttemptResult, QuizResultsResponse
from src.app.repository.question_repository import QuestionRepository
from src.app.repository.quiz_repository import QuizRepository

from typing import List
import json 
import logging

question_router = APIRouter()

@question_router.post("/upload-questions")
async def upload_questions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        data = json.loads(contents.decode('utf-8'))
        
        question_service = QuestionService(db)
        
        for question_data in data["questions"]:
            logging.info(f"Processing question: {question_data}")
            existing_question = question_service.get_question_by_text(question_data["question_text"], question_data["language"])
            if existing_question:
                logging.info(f"Skipping duplicate question: {question_data['question_text']}")
                continue  # Skip if the question already exists
            question = question_service.create_question_from_json(question_data)
            question_service.add(question)
        
        return {"message": "Questions uploaded successfully"}
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing file: {e}")

@question_router.get("/questions", response_model=List[QuestionResponse])
def get_questions_by_language_and_difficulty(language: str, difficulty: str, db: Session = Depends(get_db)):
    question_service = QuestionService(db)
    questions = question_service.get_questions_by_language_and_difficulty(language, difficulty)
    if not questions:
        raise HTTPException(status_code=404, detail="Questions not found for the given language and difficulty")
    return questions

