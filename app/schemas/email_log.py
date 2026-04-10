from pydantic import BaseModel, ConfigDict
from app.models.email_log import EmailLogStatus
from datetime import datetime

class EmailLogShort(BaseModel):
    id: int
    to: list[str]
    subject: str | None
    status: str

    model_config = ConfigDict(from_attributes = True)

class EmailLogList(BaseModel):
    items: list[EmailLogShort]
    total: int
    limit: int
    offset: int

class EmailLogItem(BaseModel):
    status: EmailLogStatus
    from_email: str
    to: list[str]
    cc: list[str] = []
    bcc: list[str] = []
    subject: str
    body: str
    files_data: list[dict] | None
    created_at: datetime
    sent_at: datetime | None
    error_message: str | None

    model_config = ConfigDict(from_attributes = True)
