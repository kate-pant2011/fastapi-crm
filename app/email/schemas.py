from pydantic import BaseModel, EmailStr, ConfigDict, Field

class EmailPostRequest(BaseModel):
    login: EmailStr 
    password: str = Field(min_length=1)
    server: str | None = Field(None, min_length=1)
    port: int | None = Field(None, gt=0)
    assigned_user_id: int | None = Field(None, gt=0)


class EmailPatchRequest(BaseModel):
    login: EmailStr = Field(None, min_length=1)
    password: str = Field(None, min_length=1)
    server: str | None = Field(None, min_length=1)
    port: int | None = Field(None, gt=0)
    owner_id: int | None = Field(None, gt=0)

    model_config = {"extra": "forbid"}


class EmailStatusResponse(BaseModel):
    status: str


class EmailShortResponse(BaseModel):
    id: int
    login: EmailStr

    model_config = ConfigDict(from_attributes = True)


class EmailListResponse(BaseModel):
    items: list[EmailShortResponse]
    total: int
    limit: int
    offset: int


class EmailItem(BaseModel):
    id: int
    login: EmailStr
    server: str
    port: int
    owner_id: int | None
    creator_id: int

    model_config = ConfigDict(from_attributes = True)