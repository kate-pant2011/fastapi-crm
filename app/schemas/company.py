from pydantic import BaseModel, Field
from app.schemas.contract import ContractItem
from app.schemas.common import BaseShortResponse


class CompanyItem(BaseModel):
    name: str
    inn: str
    client: BaseShortResponse
    contracts: list[ContractItem]

    class Config:
        from_attributes = True


class CompanyPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    model_config = {"extra": "forbid"}


class CompanyCreation(BaseModel):
    name: str
    inn: str
    client_id: int
