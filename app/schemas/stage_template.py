from pydantic import BaseModel
from app.schemas.common import BaseShortResponse


class StageTemplateItem(BaseModel):
    name: str
    stage_list: list[str]
    creator: BaseShortResponse

    class Config:
        from_attributes = True


class StageTemplateCreation(BaseModel):
    name: str
    stage_list: list[str]


class StageTemplatePatchRequest(BaseModel):
    stage_list: list[str]
