from fastapi import APIRouter, Depends
from src.app.services.user_service import UserService
from src.app.repository.user_repository import UserRepository
from sqlalchemy.orm import Session
from src.app.config.database import get_db
from src.app.schemas.user_schemas import UserResponse

user_router = APIRouter()

@user_router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(UserRepository(db))
    user = user_service.get_user(user_id)
    return user
