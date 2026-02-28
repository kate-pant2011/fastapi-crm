from .base import BaseModel
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY


class Stage(BaseModel):
    __tablename__ = "stages"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    project = relationship("Project", back_populates="stages")
    assignments = relationship("Assignment", back_populates="stage")


class StageTemplate(BaseModel):
    __tablename__ = "stage_templates"

    name = Column(String, nullable=False, unique=True)
    stage_list = Column(ARRAY(String), nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    creator = relationship("User", back_populates="stage_templates")
    
