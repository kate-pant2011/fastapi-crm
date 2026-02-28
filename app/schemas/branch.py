from pydantic import BaseModel
from app.schemas.base import ShortItem


class BranchItem(BaseModel):
    name: str
    inn: str
    users: list[ShortItem] | None

    class Config:
        from_attributes = True


class BranchCreationRequest(BaseModel):
    inn: str
    name: str



