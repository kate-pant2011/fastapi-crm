import os
from dotenv import load_dotenv
from datetime import datetime, UTC

MANAGEMENT_ROLES = {
    "admin", "manager", "owner"
}

VALID_MODES = {
    "management", "execution",
}

class ApplicationException(Exception):
    def __init__(self, error_name: str, error_code: int, payload: dict | None = None):
        super().__init__(error_name)
        self.name = error_name
        self.code = error_code
        self.payload = payload


now = datetime.now(UTC)


class Settings:
    def __init__(self):
        load_dotenv()
        secret = os.getenv("SECRET_KEY")
        if not secret:
            raise RuntimeError("No secret_key")
        self._secret_key = secret

        database = os.getenv("DATABASE_URL")
        if not database:
            raise RuntimeError("No data base url")
        
        self._database_url = database

        alembic_db = os.getenv("ALEMBIC_URL")
        if not alembic_db:
            raise RuntimeError("No data base url")
        
        self._alembic_url = alembic_db

        fernet_key = os.getenv("FERNET_KEY")
        if not fernet_key:
            raise RuntimeError("No fernet key")

        self._fernet_key = fernet_key

        email_user = os.getenv("EMAIL_USER")
        if not email_user:
            raise RuntimeError("No email_user")
        
        self._email_user = email_user

        email_password = os.getenv("EMAIL_PASSWORD")
        if not email_password:
            raise RuntimeError("No email_password")
        
        self._email_password = email_password

        self.PROJECT_NAME: str = "My CRM"
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        self.RESET_TOKEN_EXPIRE_MINUTES: int = 15
        self.REFRESH_TOKEN_EXPIRE_DAYS: int = 3
        self.SMTP_HOST: str = "smtp.yandex.ru"
        self.SMTP_PORT: int = 465

    @property
    def SECRET_KEY(self):
        return self._secret_key

    @property
    def DATABASE_URL(self):
        return self._database_url

    @property
    def ALEMBIC_URL(self):
        return self._alembic_url
    
    @property
    def FERNET_KEY(self):
        return self._fernet_key
    
    @property
    def EMAIL_USER(self):
        return self._email_user
    
    @property
    def EMAIL_PASSWORD(self):
        return self._email_password
    


settings = Settings()
