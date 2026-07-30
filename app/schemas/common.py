from pydantic import BaseModel, ConfigDict, Field
from typing import Type


def to_schema(pydantic_item: Type[BaseModel], orm_obj):
    return pydantic_item.model_validate(orm_obj)


class BaseShortResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes = True)


class BaseListResponse(BaseModel):
    items: list[BaseShortResponse]
    total: int
    limit: int
    offset: int


class BaseCountResponse(BaseModel):
    name: str
    total: int
    

class LegalEntityShortResponse(BaseModel):
    id: int
    name: str
    inn: str

class LegalEntityListResponse(BaseModel):
    items: list[LegalEntityShortResponse]
    total: int
    limit: int
    offset: int


class OrganizationPatchRequest(BaseModel):
    name: str | None = Field(None, min_length=1)

    kpp: str | None = None
    ogrn: str | None = None
    okpo: str | None = None
    okved: str |None = None
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