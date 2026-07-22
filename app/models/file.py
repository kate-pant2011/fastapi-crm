from .base import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

class File(BaseModel):
    __tablename__ = "files"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    template_id = Column(Integer, ForeignKey("document_templates.id", ondelete="CASCADE"), nullable=True)

    name = Column(String(255), nullable=False) # original filename
    unique_name = Column(String(255), nullable=False) # filename created with uuid
    path = Column(String(500), nullable=False)
    size = Column(BigInteger, nullable=False)
    mime_type = Column(String(255), nullable=False)

    creator = relationship("User", back_populates="files")
    client = relationship("Client", back_populates="files")
    project = relationship("Project", back_populates="files")
    template = relationship("DocumentTemplate", back_populates="file")
    generated_document = relationship(
        "GeneratedDocument", back_populates="file", cascade="all, delete-orphan", uselist=False, passive_deletes=True
    )


