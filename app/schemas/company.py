from pydantic import BaseModel
from app.schemas.contract import ContractItem
from app.schemas.base import ShortItem


class CompanyItem(BaseModel):
    name: str
    inn: str
    contracts: list[ContractItem]

    class Config:
        from_attributes = True

class CompanyCreation(BaseModel):
    name: str
    inn: str
    client_id: int




