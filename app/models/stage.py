from .base import BaseModel
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship


class Stage(BaseModel):
    __tablename__ = "stages"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    position = Column(Integer, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)

    project = relationship("Project", back_populates="stages")
    assignments = relationship("Assignment", back_populates="stage")
