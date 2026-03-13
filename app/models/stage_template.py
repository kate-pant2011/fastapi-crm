from .base import BaseModel
from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY


class StageTemplate(BaseModel):
    __tablename__ = "stage_templates"

    name = Column(String(255), nullable=False, unique=True, index=True)
    stage_list = Column(ARRAY(String(255)), nullable=False)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    creator = relationship("User", back_populates="stage_templates")
