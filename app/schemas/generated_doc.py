from pydantic import BaseModel, Field, EmailStr

class GeneratedItem(BaseModel):
    id: int
    file_id: int
    template_id: int | None
    creator_id: int
    filename: str

class GeneratedListResponse(BaseModel):
    items: list[GeneratedItem]
    total: int
    limit: int
    offset: int

class GeneratedDocSend(BaseModel):
    email_id: int
    to: str
    cc: str | None = Field(None, min_length=1) 
    bcc: str | None = Field(None, min_length=1) 
    subject: str |None = Field(None, min_length=1) 
    body: str | None = Field(None, min_length=1)