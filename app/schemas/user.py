from pydantic import BaseModel, EmailStr

class UserItem(BaseModel):
    id: int
    name: str
    surname: str
    position: str

    class Config:
        from_attributes = True

class UserCard(BaseModel):
    name: str
    surname: str
    position: str
    email: str
    branch: str
    roles: list[str]

class UserCreationRequest(BaseModel):
    name: str
    surname: str
    position: str
    email: EmailStr
    role: list[str]
    branch_inn: str

class UserCreationResponse(BaseModel):
    email: EmailStr
    password: str

class UserDeletionResponse(BaseModel):
    result: bool

class RecoveryResponse(BaseModel):
    result: bool