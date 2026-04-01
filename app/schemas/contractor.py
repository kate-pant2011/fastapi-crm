from pydantic import BaseModel, EmailStr, Field


class ContractorItem(BaseModel):
    name: str
    email: list[str] | None
    description: str

    class Config:
        from_attributes = True


class ContractorPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    email: list[EmailStr] | None = Field(None, min_items=1)
    description: str | None = Field(None, min_length=1)
    model_config = {"extra": "forbid"}


class ContractorCreation(BaseModel):
    name: str = Field(min_length=1)
    email: list[EmailStr] | None = Field(None, min_items=1)
    description: str = Field(min_length=1)
    model_config = {"extra": "forbid"}
