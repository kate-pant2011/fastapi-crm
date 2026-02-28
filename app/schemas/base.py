from pydantic import BaseModel
from typing import Type

def to_schema(pydantic_item: Type[BaseModel], orm_obj):
    return pydantic_item.model_validate(orm_obj)

from pydantic import BaseModel

class ShortItem(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True