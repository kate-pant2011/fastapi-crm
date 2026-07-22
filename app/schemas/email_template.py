from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import BaseShortResponse


class EmailTemplateItem(BaseModel):
    name: str
    subject_content: str
    body_content: str
    is_public: bool
    creator: BaseShortResponse

    model_config = ConfigDict(from_attributes = True)


class EmailTemplateShortItem(BaseModel):
    subject: str | None
    body: str | None


class EmailTemplateCreation(BaseModel):
    name: str = Field(min_length=1)
    subject_content: str | None = Field(None, min_length=1)
    body_content: str | None = Field(None, min_length=1)
    is_public: bool
    model_config = {"extra": "forbid"}


class EmailTemplatePatchRequest(BaseModel):
    subject_content: str | None = Field(None, min_length=1)
    body_content: str | None = Field(None, min_length=1)
    is_public: bool | None 
    model_config = {"extra": "forbid"}

class EmailTemplateDeleteResponse(BaseModel):
    name: str

