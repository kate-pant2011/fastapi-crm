from pydantic import BaseModel
from app.schemas.base import ShortItem
from datetime import datetime


class StageItem(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    project: ShortItem

    class Config:
        from_attributes = True


class StageCreation(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    project_id: int 

class StageTemplateItem(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class StageTemplateCreation(BaseModel):
    name: str
    stage_list: list[str]
