from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import BaseShortResponse
from app.email.schemas import EmailShortResponse


class EmailTemplateItem(BaseModel):
    name: str
    subject_content: str | None
    body_content: str | None
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
    from_emails: list[str] | None = Field(None, min_items=1)
    is_public: bool
    model_config = {"extra": "forbid"}


class EmailTemplatePatchRequest(BaseModel):
    subject_content: str | None = Field(None, min_length=1)
    body_content: str | None = Field(None, min_length=1)
    from_emails: list[str] | None = Field(None, min_items=1) 
    is_public: bool | None 
    model_config = {"extra": "forbid"}

class EmailTemplateDeleteResponse(BaseModel):
    name: str


class EmailRenderDTO(BaseModel):
    from_emails: list[EmailShortResponse]
    to: str | None
    cc: str | None
    bcc: str | None = None
    subject: str | None
    body: str | None
