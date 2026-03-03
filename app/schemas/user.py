from pydantic import BaseModel, EmailStr
from app.schemas.common import ShortItem


class UserItem(BaseModel):
    name: str
    surname: str
    position: str
    email: str
    branch: ShortItem
    roles: list[ShortItem]
    clients: list[ShortItem] | None
    assignments: list[ShortItem] | None

    class Config:
        from_attributes = True


class UserCreationRequest(BaseModel):
    name: str
    surname: str
    position: str
    email: EmailStr
    role: list[str]
    branch_id: int


class UserCreationResponse(BaseModel):
    name: str
    password: str
