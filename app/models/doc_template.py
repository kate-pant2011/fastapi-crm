from .base import BaseModel
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, ARRAY
from sqlalchemy.orm import relationship


class DocumentTemplate(BaseModel):
    __tablename__ = "document_templates"
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True, unique=False)

    variables = Column(ARRAY(String(255)), nullable=True)
    required_entities = Column(ARRAY(String(255)), nullable=True)
    is_public = Column(Boolean, nullable=False)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    creator = relationship("User", back_populates="document_templates")
    generated_documents = relationship("GeneratedDocument", back_populates="template")
    file = relationship(
        "File",
        back_populates="template", 
        uselist=False, 
        passive_deletes=True
    )
