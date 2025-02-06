from src.app.repository.user_repository import UserRepository
from src.app.models.user import User
from src.app.schemas.user_schemas import UserResponse
from src.app.utils.utils import hash_password
from fastapi import HTTPException

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user(self, user_id: int) -> UserResponse:
        user = self.user_repository.get_user_by_id(user_id)
        return UserResponse.from_orm(user) if user else None

    def create_user(self, username: str, hashed_password: str, is_admin: bool, role: str) -> UserResponse:
        user = self.user_repository.create_user(username, hashed_password, is_admin, role)
        return UserResponse.from_orm(user)