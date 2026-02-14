from passlib.hash import bcrypt
import jwt 
from .config import settings
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException


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

    def create_access(self, sub, roles): 
        exp = datetime.now(timezone.utc)  + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(sub), "exp": exp, "role": roles} 
        encoded = jwt.encode(payload, self.key, self.algorithm) 
        return encoded

    def create_refresh(self, sub, jti):
        exp = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {"sub": str(sub), "exp": exp, "jti": jti} 
        encoded = jwt.encode(payload, self.key, self.algorithm) 
      
        return RefreshDTO(
            token=encoded,
            exp=exp
        )
    
    def decode_token(self, token: str):
        try:
            decoded = jwt.decode(
                token,
                self.key,
                algorithms=self.algorithm
            )

            if decoded.get("jti") is None:
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            exp = datetime.fromtimestamp(decoded.get("exp"), tz=timezone.utc)

            return DecodeDTO(
                jti=decoded.get("jti"),
                exp=exp
            )
        
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

def check_password(password):
    letter = 0
    digit = 0

    if len(password) >= 8 and len(password) <= 16:
        if str.isascii(password):
            for p in password:
                if p.isdigit():
                    digit += 1
                elif p.isalpha:
                    letter += 1
        else:
            return "includes forbidden symbols"
    else:
        return "is too short/long"

    if letter > 0 and digit > 0:
        return None
    else:
        return "does not include letters/digits"