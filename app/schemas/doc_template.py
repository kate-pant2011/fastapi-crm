from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import BaseShortResponse


class DocTemplateItem(BaseModel):
    name: str
    description: str | None
    required_entities: list[str] | None
    variables: list[str] | None
    is_public: bool
    creator: BaseShortResponse
    file: BaseShortResponse

    model_config = ConfigDict(from_attributes = True)


class DocTemplateCreation(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = Field(None, min_length=1)
    required_entities: list[str] | None = Field(None, min_items=1)
    is_public: bool
    model_config = {"extra": "forbid"}


class DocTemplatePatchRequest(BaseModel):
    description: str | None = Field(None, min_length=1)
    required_entities: list[str] | None = Field(None, min_items=1)
    is_public: bool | None 
    model_config = {"extra": "forbid"}


class DocTemplateDeleteResponse(BaseModel):
    result: str

class GeneratedDocResponse(BaseModel):
    doc_id: int
    file_id: int
    filename: str