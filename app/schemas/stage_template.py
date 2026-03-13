from pydantic import BaseModel, Field
from app.schemas.common import BaseShortResponse


class StageTemplateItem(BaseModel):
    name: str
    stage_list: list[str]
    creator: BaseShortResponse

    class Config:
        from_attributes = True


class StageTemplateCreation(BaseModel):
    name: str = Field(min_length=1)
    stage_list: list[str] = Field(min_items=1)
    model_config = {"extra": "forbid"}


class StageTemplatePatchRequest(BaseModel):
    stage_list: list[str]
    model_config = {"extra": "forbid"}
