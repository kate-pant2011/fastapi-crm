from .base import BaseModel
from sqlalchemy import Column, String, Integer, Boolean, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class EmailTemplate(BaseModel):
    __tablename__ = "email_templates"
    name = Column(String(255), nullable=False, unique=True, index=True)
    subject_content = Column(String(500), nullable=True)
    body_content = Column(Text, nullable=True)
    is_public = Column(Boolean, nullable=False)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    creator = relationship("User", back_populates="email_templates")