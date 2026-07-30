from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.contract import ContractItem
from app.schemas.common import BaseShortResponse


class ProjectItem(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    client_name: str
    client_email: list[str]
    client_id: int 
    contract: ContractItem | None
    manager: BaseShortResponse
    stages: list[BaseShortResponse] | None
    is_archived: bool
    files: int | None


class ProjectPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    start_date: datetime | None = None
    end_date: datetime | None = None
    contract_id: int | None = Field(None, gt=0)

    model_config = {"extra": "forbid"}


class ProjectCreation(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    start_date: datetime
    end_date: datetime
    client_id: int = Field(gt=0)

    model_config = {"extra": "forbid"}
