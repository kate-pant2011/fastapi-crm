from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.common import BaseShortResponse
from typing import Literal

statusname = Literal["draft", "pending", "signed", "expired", "terminated"]


class ContractItem(BaseModel):
    id: int
    number: str
    status: str

    class Config:
        from_attributes = True


class ContractListResponse(BaseModel):
    items: list[ContractItem]
    total: int
    limit: int
    offset: int


class ContractPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    number: str | None = Field(None, min_length=1)
    status: statusname | None
    description: str | None = Field(None, min_length=1)
    valid_from: datetime | None = None
    valid_to: datetime | None = None

    model_config = {"extra": "forbid"}


class GetContractItem(BaseModel):
    number: str
    status: statusname
    name: str | None
    description: str | None
    valid_from: datetime | None
    valid_to: datetime
    branch: BaseShortResponse
    company: BaseShortResponse
    is_archived: bool

    class Config:
        from_attributes = True


class СontractCreation(BaseModel):
    number: str = Field(min_length=1)
    status: statusname
    name: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    valid_from: datetime | None
    valid_to: datetime
    company_id: int = Field(gt=0)
    branch_id: int = Field(gt=0)

    model_config = {"extra": "forbid"}