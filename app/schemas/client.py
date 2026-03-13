from pydantic import BaseModel, EmailStr, Field
from app.schemas.common import BaseShortResponse


class ClientItem(BaseModel):
    name: str
    email: list[str] | None
    telephone: list[str] | None
    manager: BaseShortResponse
    projects: list[BaseShortResponse] | None
    companies: list[BaseShortResponse] | None

    class Config:
        from_attributes = True


class ClientPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    email: list[str] | None = Field(None, min_items=1)
    telephone: list[str] | None = Field(None, min_items=1)
    manager_id: int | None = Field(None, gt=0)
    model_config = {"extra": "forbid"}


class ClientCreation(BaseModel):
    name: str
    email: list[EmailStr] | None
    telephone: list[str] | None
