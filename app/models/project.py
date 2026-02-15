from datetime import datetime
from .base import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

class Project(BaseModel):
    __tablename__ = "projects"

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    contract = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    client = relationship("Client", back_populates="projects")
    stages = relationship("Stage", back_populates="project")