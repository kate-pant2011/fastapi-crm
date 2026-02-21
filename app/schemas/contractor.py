from pydantic import BaseModel, EmailStr

class ContractorItem(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class GetContractor(BaseModel):
    name: str
    email: list[str] | None 
    description: str
    contractor_companies: list[str] | None 

class ContractorCreation(BaseModel):
    name: str
    email: list[EmailStr] | None
    description: str
    contractor_inn: str | None

class CreationResponse(BaseModel):
    contractor_id: int
    name: str

class DeletionResponse(BaseModel):
    result: bool

class RecoveryResponse(BaseModel):
    result: bool