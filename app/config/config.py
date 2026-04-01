import os
from dotenv import load_dotenv
from datetime import datetime, UTC


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
        secret = os.environ.pop("SECRET_KEY")
        if not secret:
            raise RuntimeError("No secret_key")
        self._secret_key = secret

        database = os.environ.pop("DATABASE_URL")
        if not database:
            raise RuntimeError("No data base url")
        
        self._database_url = database

        fernet_key = os.environ.pop("FERNET_KEY")
        if not fernet_key:
            raise RuntimeError("No fernet key")

        self._fernet_key = fernet_key

        self.PROJECT_NAME: str = "My CRM"
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        self.REFRESH_TOKEN_EXPIRE_DAYS: int = 3

    @property
    def SECRET_KEY(self):
        return self._secret_key

    @property
    def DATABASE_URL(self):
        return self._database_url
    
    @property
    def FERNET_KEY(self):
        return self._fernet_key


settings = Settings()
