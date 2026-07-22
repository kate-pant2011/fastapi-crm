from pydantic import BaseModel, Field
from app.schemas.contract import ContractItem
from app.schemas.common import BaseShortResponse


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


class CompanyPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)

    kpp: str | None = None
    ogrn: str | None = None
    okpo: str | None = None
    okved: str | None = None
    okfs: str | None = None
    okopf: str | None = None
    okato: str | None = None

    legal_address: str | None = None
    address: str | None = None

    email: str | None = None
    telephone: str | None = None
    website: str | None = None

    director_full_name: str | None = None
    director_short_name: str | None = None
    director_position: str | None = None
    authority_document: str | None = None

    bank_name: str | None = None
    bik: str | None = None
    checking_account: str | None = None
    correspondent_account: str | None = None

    model_config = {"extra": "forbid"}