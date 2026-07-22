from pydantic import BaseModel, Field
from app.schemas.common import BaseShortResponse
from app.schemas.stage import ShortStageResponse

class AssignmentItem(BaseModel):
    name: str
    description: str
    stage: ShortStageResponse
    contractor: BaseShortResponse | None
    user: BaseShortResponse | None
    
    class Config:
        from_attributes = True


class AssignmentPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    is_done: bool | None = None
    model_config = {"extra": "forbid"}


class AssignmentCreation(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    stage_id: int = Field(gt=0)
    user_id: int | None = Field(None, gt=0)
    contractor_id: int | None = Field(None, gt=0)

    model_config = {"extra": "forbid"}