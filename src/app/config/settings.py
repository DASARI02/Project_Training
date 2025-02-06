from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:Chaitu%402002@localhost/quiz_db" 
    secret_key: str = "your_secret_key"
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 30 

    class Config: 
        env_file = ".env"

settings = Settings()
   