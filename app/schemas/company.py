from pydantic import BaseModel, Field
from app.schemas.contract import ContractItem
from app.schemas.common import BaseShortResponse, OrganizationPatchRequest


class CompanyCreation(BaseModel):
    name: str = Field(min_length=1)
    inn: str = Field(min_length=1)
    client_id: int = Field(gt=0)
    model_config = {"extra": "forbid"}


class CompanyItem(BaseModel):
    name: str
    inn: str
    client: BaseShortResponse
    contracts: list[ContractItem]
    is_archived: bool

    kpp: str | None
    ogrn: str | None
    okpo: str | None
    okved: str | None
    okfs: str | None
    okopf: str | None
    okato: str | None

    legal_address: str | None
    address: str | None

    email: str | None
    telephone: str | None
    website: str | None

    director_full_name: str | None
    director_short_name: str | None
    director_position: str | None
    authority_document: str | None

    bank_name: str | None
    bik: str | None
    checking_account: str | None 
    correspondent_account: str | None

    class Config:
        from_attributes = True


class CompanyPatchRequest(OrganizationPatchRequest):
    pass