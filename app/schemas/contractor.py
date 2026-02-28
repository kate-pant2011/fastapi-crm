from pydantic import BaseModel, EmailStr
from app.schemas.base import ShortItem


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


class ContractorCreation(BaseModel):
    name: str
    email: list[EmailStr] | None
    description: str


