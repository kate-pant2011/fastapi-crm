from passlib.hash import bcrypt
import jwt
from .config import settings
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from fastapi import HTTPException
from cryptography.fernet import Fernet

key = settings.FERNET_KEY
cipher = Fernet(key)

def encrypt_password(password):
    encrypted = cipher.encrypt(password.encode())
    return encrypted

def decrypt_password(encrypted_password):
    key = settings.FERNET_KEY
    cipher = Fernet(key)
    decrypt = cipher.decrypt(encrypted_password).decode()
    return decrypt


@dataclass
class RefreshDTO:
    token: str
    exp: datetime


@dataclass
class DecodeDTO:
    jti: str
    exp: datetime


class JWTService:
    def __init__(self):
        self.algorithm = settings.ALGORITHM
        self.key = settings.SECRET_KEY

    def create_access(self, sub, roles, status, active):
        exp = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sub": str(sub),
            "exp": exp,
            "roles": roles,
            "status": status,
            "active": active,
        }
        encoded = jwt.encode(payload, self.key, self.algorithm)
        return encoded

    def create_refresh(self, sub, jti):
        exp = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload = {"sub": str(sub), "exp": exp, "jti": jti}
        encoded = jwt.encode(payload, self.key, self.algorithm)

        return RefreshDTO(token=encoded, exp=exp)

    def decode_token(self, token: str):
        try:
            decoded = jwt.decode(token, self.key, algorithms=self.algorithm)

            if decoded.get("jti") is None:
                raise HTTPException(status_code=401, detail="Invalid token type")

            exp = datetime.fromtimestamp(decoded.get("exp"), tz=timezone.utc)

            return DecodeDTO(jti=decoded.get("jti"), exp=exp)

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")

        except jwt.PyJWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


def hash_password(password):
    hashed_password = bcrypt.hash(password)
    return hashed_password


def verify_password(password, stored_hash):
    ans = bcrypt.verify(password, stored_hash)
    return ans
