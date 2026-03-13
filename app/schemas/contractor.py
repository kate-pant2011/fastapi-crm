from pydantic import BaseModel, EmailStr, Field


class ContractorContractItem(BaseModel):
    id: int
    contract_name: str | None


class ContractorItem(BaseModel):
    name: str
    email: list[str] | None
    description: str
    contracts: list[ContractorContractItem] | None

    class Config:
        from_attributes = True


class ContractorPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    email: list[EmailStr] | None = Field(None, min_items=1)
    description: str | None = Field(None, min_length=1)
    model_config = {"extra": "forbid"}


class ContractorCreation(BaseModel):
    name: str
    email: list[EmailStr] | None
    description: str
