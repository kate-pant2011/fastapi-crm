from .base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Assignment(BaseModel):
    __tablename__ = "assignments"

    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False, index=True) 
    contractor_id = Column(Integer, ForeignKey("contractors.id"), nullable=True, index=True) 
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True) 

    name = Column(String, nullable=False)
    description = Column(String)

    contractor = relationship("Contractor", back_populates="assignments")
    stage = relationship("Stage", back_populates="assignments")
    user = relationship("User", back_populates="assignments")

