from pydantic import BaseModel
from datetime import datetime
from app.schemas.contract import ContractItem
from app.schemas.common import ShortItem


class ProjectItem(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    client_name: str
    client_email: list[str]
    contract: ContractItem | None
    manager: ShortItem
    stages: list[ShortItem] | None


class ProjectCreation(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    client_id: int
    contract_id: int | None
