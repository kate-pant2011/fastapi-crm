from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class InnRequest(BaseModel):
    inn: int

class InnResponse(BaseModel):
    inn: int
    can_signup: bool
    company: str | None
    reason: str | None

class SignupRequest(BaseModel):
    inn: int
    company: str 
    login: EmailStr
    password: str
    name: str
    surname: str
    position: str

class SignupResponse(BaseModel):
    company: str
    login: str
    reason: str | None

