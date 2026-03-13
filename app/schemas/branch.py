from pydantic import BaseModel, Field
from app.schemas.common import BaseShortResponse


class BranchItem(BaseModel):
    name: str
    inn: str
    users: list[BaseShortResponse] | None

    class Config:
        from_attributes = True


class BranchPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    model_config = {"extra": "forbid"}


class BranchCreationRequest(BaseModel):
    inn: str = Field(min_length=1)
    name: str = Field(min_length=1)

    model_config = {"extra": "forbid"}