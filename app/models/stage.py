from .base import BaseModel
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship

class Stage(BaseModel):
    __tablename__ = "stages"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    name = Column(String)
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_deleted = Column(Boolean, default=False, nullable=False)

    project = relationship("Project", back_populates="stages")
    assignments = relationship("Assignment", back_populates="stage")