from datetime import timedelta, datetime
from typing import Optional
from jose import JWTError, jwt
from src.app.config.settings import settings
from src.app.repository.user_repository import UserRepository
from src.app.models.user import User
from src.app.schemas.user_schemas import UserLogin, UserCreate
from src.app.utils.utils import hash_password, verify_password

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        to_encode["sub"] = str(to_encode["sub"]) 
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expires_minutes))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repository.get_user_by_username(username)
        if user and verify_password(password, user.hashed_password):
            return user
        return None

    def register_user(self, user_create: UserCreate):
        hashed_password = hash_password(user_create.password)
        return self.user_repository.create_user(user_create.username, hashed_password, is_admin=False, role="student")