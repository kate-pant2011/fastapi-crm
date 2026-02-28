from pydantic import BaseModel, EmailStr
from app.schemas.base import ShortItem


class ClientItem(BaseModel):
    name: str
    email: list[str] | None
    telephone: list[str] | None
    projects: list[ShortItem] | None
    companies: list[ShortItem] | None

    class Config:
        from_attributes = True


class ClientCreation(BaseModel):
    name: str
    email: list[EmailStr] | None
    telephone: list[str] | None


