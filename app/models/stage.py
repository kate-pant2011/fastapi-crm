from datetime import datetime
from .base import BaseModel
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import relationship

class Stage(BaseModel):
    __tablename__ = "stages"

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String)
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    project = relationship("Project", back_populates="stages")
    executors = relationship("Executor", back_populates="stage", cascade="all, delete-orphan")