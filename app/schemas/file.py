from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.common import BaseShortResponse

class FileItem(BaseModel):
    id: int
    name: str
    size: int
    mime_type: str
    creator: BaseShortResponse
    client: BaseShortResponse | None
    project: BaseShortResponse | None

    class Config:
        from_attributes = True

class FileDeleteResponse(BaseModel):
    deleted: bool