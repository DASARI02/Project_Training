from fastapi import FastAPI
from src.app.router.auth_router import auth_router
from src.app.router.quiz_router import quiz_router
from src.app.router.user_router import user_router
from src.app.router.question_router import question_router
from src.app.config.database import engine, Base
from sqlalchemy.orm import registry, configure_mappers

app = FastAPI()

configure_mappers()

mapper_registry = registry()
mapper_registry.configure()

Base.metadata.create_all(bind=engine)

print("Starting the quiz!")

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(quiz_router, prefix="/quizzes", tags=["Quiz"])
app.include_router(user_router, prefix="/users", tags=["User"])
app.include_router(question_router, prefix="/questions", tags=["Questions"])