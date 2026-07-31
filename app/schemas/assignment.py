from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import BaseShortResponse
from app.schemas.stage import ShortStageResponse
from datetime import datetime


class AssignmentShortResponse(BaseModel):
    id: int
    name: str
    description: str
    deadline: datetime
    model_config = ConfigDict(from_attributes = True)


class AssignmentListResponse(BaseModel):
    items: list[AssignmentShortResponse]
    total: int
    limit: int
    offset: int


class AssignmentItem(BaseModel):
    name: str
    description: str
    is_done: bool
    stage: ShortStageResponse
    contractor: BaseShortResponse | None
    user: BaseShortResponse | None
    
    class Config:
        from_attributes = True


class AssignmentPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    is_done: bool | None = None
    deadline: datetime | None = None
    model_config = {"extra": "forbid"}


class AssignmentCreation(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    stage_id: int = Field(gt=0)
    user_id: int | None = Field(None, gt=0)
    contractor_id: int | None = Field(None, gt=0)
    deadline: datetime | None = None

    model_config = {"extra": "forbid"}