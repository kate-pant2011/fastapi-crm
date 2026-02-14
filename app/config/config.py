import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

now = datetime.utcnow()

class Settings:
    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
            raise RuntimeError("No secret_key")
        
        self.PROJECT_NAME: str = "My CRM"       
        self.ALGORITHM: str = "HS256" 
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
        self.REFRESH_TOKEN_EXPIRE_DAYS: int = 3
        self.DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()

