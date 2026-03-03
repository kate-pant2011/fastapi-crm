from pydantic import BaseModel
from datetime import datetime
from app.schemas.common import ShortItem


class ContractItem(BaseModel):
    id: int
    number: str
    status: str

    class Config:
        from_attributes = True


class GetcontractItem(BaseModel):
    number: str
    status: str
    name: str | None
    description: str | None
    valid_from: datetime | None
    valid_to: datetime
    branch: ShortItem

    class Config:
        from_attributes = True

class contractCreation(BaseModel):
    number: str
    status: str
    name: str | None
    description: str | None
    valid_from: datetime | None
    valid_to: datetime
    company_id: int
    branch_id: int
