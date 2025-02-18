from fastapi import Depends, HTTPException, Security
from src.app.auth.jwt_bearer import JWTBearer
from src.app.repository.user_repository import UserRepository
from sqlalchemy.orm import Session
from src.app.config.database import get_db
from src.app.models.user import User

jwt_bearer = JWTBearer()

def get_current_user(token: str = Security(jwt_bearer), db: Session = Depends(get_db)):
    payload = jwt_bearer.verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("sub")
    username = payload.get("username")
    role = payload.get("role")
    user_repository = UserRepository(db)
    user = user_repository.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    print(user_id)
    return {"user": user, "username": username, "role": role}


def get_current_active_user(current_user: dict = Security(get_current_user)):
    user = current_user["user"]
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_admin_user(current_user: dict = Security(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user["user"]

def get_current_student_user(current_user: dict = Security(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user["user"]