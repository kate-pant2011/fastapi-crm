from pydantic import BaseModel, ConfigDict
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
    items: list[BaseShortResponse]
    total: int
    limit: int
    offset: int


