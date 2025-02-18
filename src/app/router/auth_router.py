from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.app.schemas.user_schemas import UserLogin, UserCreate, UserResponse
from src.app.services.auth_service import AuthService
from src.app.repository.user_repository import UserRepository
from src.app.config.database import get_db
from datetime import timedelta
from src.app.config.settings import settings
from datetime import datetime

auth_router = APIRouter()

@auth_router.post("/register/", response_model=UserResponse)
def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    return auth_service.register_user(user_create)

@auth_router.post("/token")
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    auth_service = AuthService(UserRepository(db))
    user = auth_service.authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=settings.access_token_expires_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }