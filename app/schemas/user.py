from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.schemas.common import BaseShortResponse
from typing import Literal


class UserItem(BaseModel):
    name: str
    surname: str
    position: str
    email: str
    branch: BaseShortResponse
    roles: list[BaseShortResponse]
    clients: list[BaseShortResponse] | None
    assignments: list[BaseShortResponse] | None

    class Config:
        from_attributes = True


rolename = Literal["owner", "admin", "manager", "executor"]


class UserPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    surname: str | None = Field(None, min_length=1)
    position: str | None = Field(None, min_length=1)
    branch_id: int | None = Field(None, gt=0)
    role: list[rolename] | None = Field(None, min_items=1)
    is_active: bool | None = None

    model_config = {"extra": "forbid"}


class UserCreationRequest(BaseModel):
    name: str = Field(min_length=1)
    surname: str = Field(min_length=1)
    position: str = Field(min_length=1)
    email: EmailStr 
    branch_id: int = Field(gt=0)
    roles: list[rolename] = Field(min_items=1)

    model_config = {"extra": "forbid"}


class UserCreationResponse(BaseModel):
    name: str
    password: str

