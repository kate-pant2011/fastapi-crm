from pydantic import BaseModel, EmailStr
from app.schemas.common import ShortItem


class AssignmentItem(BaseModel):
    name: str
    description: str 
    stage: ShortItem 
    contractor: ShortItem | None
    user: ShortItem | None

    class Config:
        from_attributes = True


class AssignmentCreation(BaseModel):
    name: str
    description: str 
    stage_id: int
    user_id: int | None
    contractor_id: int | None
