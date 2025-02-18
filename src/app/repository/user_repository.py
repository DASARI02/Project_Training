from sqlalchemy.orm import Session
from src.app.models.user import User
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

class UserRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_user_by_id(self, user_id: int) -> User:
        return self.db_session.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> User:
        return self.db_session.query(User).filter(User.username == username).first()
    
    def create_user(self, username: str, hashed_password: str, role: str = "student") -> User:
        existing_user = self.get_user_by_username(username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        user = User(username=username, hashed_password=hashed_password, role=role)
        self.db_session.add(user)
        try:
            self.db_session.commit()
            self.db_session.refresh(user)
        except IntegrityError:
            self.db_session.rollback()
            raise HTTPException(status_code=400, detail="Username already exists")
        return user