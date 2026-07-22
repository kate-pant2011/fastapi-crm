from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import BaseShortResponse
from datetime import datetime


class ShortStageResponse(BaseModel):
    id: int
    name: str
    description: str
    position: int
    start_date: datetime
    end_date: datetime
    project_id: int

    model_config = ConfigDict(from_attributes = True)


class StageListResponse(BaseModel):
    items: list[ShortStageResponse]
    total: int
    limit: int
    offset: int


class StageItem(BaseModel):
    name: str
    position: int
    description: str
    start_date: datetime
    end_date: datetime
    project: BaseShortResponse
    assignments: list[BaseShortResponse]
    is_archived: bool

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

class ReorderResultResponse(BaseModel):
    result: str