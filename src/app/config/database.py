from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Define the base class for declarative models
Base = declarative_base()

# Database URL
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:Chaitu%402002@localhost:5432/pokemon_database"

# Create the database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session management
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# get_db dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()