from .base import BaseModel
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class GeneratedDocument(BaseModel):
    __tablename__ = "generated_documents"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    template_id = Column(Integer, ForeignKey("document_templates.id"), index=True, nullable=True)

    file_id = Column(
        Integer,
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    
    creator = relationship("User", back_populates="generated_documents")
    template = relationship("DocumentTemplate", back_populates="generated_documents")
    file = relationship("File", back_populates="generated_document")