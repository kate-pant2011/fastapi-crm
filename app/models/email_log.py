from .base import BaseModel
from sqlalchemy import Column, Integer, String, ARRAY, Enum as SQLEnum, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from enum import Enum


class EmailLogStatus(Enum):
    PENDING = "pending"
    FAILED = "failed"
    SENT = "sent"

class EmailLog(BaseModel):
    __tablename__ = "email_logs"
    status = Column(
        SQLEnum(EmailLogStatus, name = "log_status_enum"), 
        nullable = False, 
        default=EmailLogStatus.PENDING
    )
    from_email = Column(String(255), nullable=False)
    to = Column(ARRAY(String), nullable=False)
    cc = Column(ARRAY(String), default=list)
    bcc = Column(ARRAY(String), default=list)
    subject = Column(String(500))
    body = Column(Text)
    files_data = Column(ARRAY(JSONB))

    error_message = Column(String, nullable=True)
    sent_at = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="email_logs")