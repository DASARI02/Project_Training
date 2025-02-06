from sqlalchemy import Column, Integer, String, Boolean, Enum
from src.app.config.database import Base
import enum

class Userrole(str, enum.Enum):
    admin = "admin"
    student = "student"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    role = Column(Enum(Userrole), default=Userrole.student)
