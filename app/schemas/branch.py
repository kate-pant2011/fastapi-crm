from pydantic import BaseModel

class BranchesItem(BaseModel):
    id: int
    name: str
    inn: str

    class Config:
        from_attributes = True

class BranchItem(BaseModel):
    name: str
    inn: str

    class Config:
        from_attributes = True

class BranchCreationRequest(BaseModel):
    inn: str
    branch_name: str

class BranchCreationResponse(BaseModel):
    inn: str
    branch_name: str
    
class BranchDeletionResponse(BaseModel):
    result: bool

class BranchRecoveryResponse(BaseModel):
    result: bool