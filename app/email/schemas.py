from pydantic import BaseModel, EmailStr, ConfigDict

class EmailPostRequest(BaseModel):
    server: str
    port: int
    login: EmailStr
    password: str
    personal: bool

class EmailPostResponse(BaseModel):
    id: int
    login: EmailStr

    model_config = ConfigDict(from_attributes = True)

class EmailLogResponse(BaseModel):
    staus: str