from pydantic import BaseModel, Field
from app.schemas.common import BaseShortResponse, OrganizationPatchRequest


class BranchCreationRequest(BaseModel):
    inn: str = Field(min_length=1)
    name: str = Field(min_length=1)

    model_config = {"extra": "forbid"}


class BranchItem(BaseModel):
    name: str
    inn: str
    users: list[BaseShortResponse] | None
    stamp_file_id: int | None
    stamp_width_mm: int | None
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
    

class BranchPatchRequest(OrganizationPatchRequest):
    stamp_width_mm: int | None = None
