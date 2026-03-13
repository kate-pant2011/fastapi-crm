from pydantic import BaseModel, Field
from app.schemas.common import BaseShortResponse
from datetime import datetime


class StageItem(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    project: BaseShortResponse
    assignments: list[BaseShortResponse]

    class Config:
        from_attributes = True


class StagePatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    start_date: datetime | None = None
    end_date: datetime | None = None

    model_config = {"extra": "forbid"}


class StageCreation(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    start_date: datetime
    end_date: datetime
    project_id: int = Field(gt=0)

    model_config = {"extra": "forbid"}


class StageReorderRequest(BaseModel):
    stages: list[int]
