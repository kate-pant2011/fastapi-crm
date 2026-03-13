from .base import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship


class Project(BaseModel):
    __tablename__ = "projects"

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True, index=True)

    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)

    client = relationship("Client", back_populates="projects")
    contract = relationship("Contract", back_populates="projects")
    stages = relationship("Stage", back_populates="project", order_by="Stage.position")
