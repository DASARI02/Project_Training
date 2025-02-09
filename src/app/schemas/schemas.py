from pydantic import BaseModel
from typing import List, Dict, Optional
from src.app.models.quiz import DifficultyLevel, LanguageEnum

class QuestionCreate(BaseModel):
    question_text: str
    options: Dict[str, str]
    correct_option: str 
    difficulty: str
    language: str

class QuestionSchema(BaseModel):
    id: int
    question_text: str
    options: dict
    language: str
    difficulty: DifficultyLevel

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: int  
    question_text: str
    options: dict
    correct_option: str
    difficulty: DifficultyLevel

    class Config:
        from_attributes = True

class QuizResponse(BaseModel):
    id: int
    title: str
    language: str
    description: str
    questions: List[QuestionResponse]

    class Config:
        from_attributes = True

class ResultSchema(BaseModel):
    question_text: str
    correct_option: str
    student_selected: str
    is_correct: bool

    class Config:
        from_attributes = True

class QuizResultsResponse(BaseModel):
    student_id: int
    total_score: int
    total_questions: int
    correct_answers: int
    results: List[ResultSchema]

    class Config:
        from_attributes = True

class QuizCreateRequest(BaseModel):
    title: str
    language: str 
    description: str
    difficulty: str
    questions: List[QuestionCreate]

class QuestionResponseWithoutAnswer(BaseModel):
    question_id: int
    question_text: str
    options: Dict[str, str]
    difficulty: str

    class Config:
        from_attributes = True

class QuizResponseWithoutAnswer(BaseModel):
    id: int
    title: str
    language: str
    description: str
    questions: List[QuestionResponseWithoutAnswer]

    class Config:
        from_attributes = True

class QuestionAttempt(BaseModel):
    question_id: int
    selected_option: str

class QuizAttempt(BaseModel):
    student_id: int
    quiz_id: int 
    attempts: List[QuestionAttempt]

class QuestionResult(BaseModel):
    question_id: int
    question_text: str
    options: Dict[str, str]
    selected_option: str
    correct_option: str 

    class Config:
        from_attributes = True

class QuestionAttemptResult(BaseModel):
    question_id: int
    question_text: str
    options: Dict[str, str]
    selected_option: str
    language: str
    difficulty: str


    class Config:
        from_attributes = True

class QuizAttemptResult(BaseModel):
    student_id: int
    results: List[QuestionResult]
    total_score: float
    total_questions: int
    correct_answers: int
    attempt_count: int 
    previous_score: Optional[float] 
    class Config:
        from_attributes = True