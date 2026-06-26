from pydantic import BaseModel, EmailStr


class LogoutResponse(BaseModel):
    result: bool


class Token(BaseModel):
    access_token: str
    refresh_token: str | None
    token_type: str
    change_password: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotLoginRequest(BaseModel):
    email: EmailStr


class RefreshRequest(BaseModel):
    refresh_token: str


class SignupRequest(BaseModel):
    inn: str
    company: str
    email: EmailStr
    password: str
    name: str
    surname: str
    position: str


class ChangePasswordRequest(BaseModel):
    password: str


class EmailResponse(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    message: str


class SignupResponse(BaseModel):
    company: str
    login: str
    reason: str | None
