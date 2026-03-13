from pydantic import BaseModel, Field
from app.schemas.common import BaseShortResponse


class AssignmentItem(BaseModel):
    name: str
    description: str
    stage: BaseShortResponse
    contractor: BaseShortResponse | None
    user: BaseShortResponse | None

    class Config:
        from_attributes = True


class AssignmentPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    model_config = {"extra": "forbid"}


class AssignmentCreation(BaseModel):
    name: str
    description: str
    stage_id: int
    user_id: int | None
    contractor_id: int | None
