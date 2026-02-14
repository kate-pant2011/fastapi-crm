from datetime import datetime
from .base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

class Executor(BaseModel):
    __tablename__ = "executors"

    stage_id = Column(Integer, ForeignKey("stages.id", ondelete="CASCADE"), nullable=False, index=True) 
    contractor_id = Column(Integer, ForeignKey("contractors.id", ondelete="CASCADE"), nullable=True, index=True) 
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True) 

    name = Column(String, nullable=False)
    description = Column(String)

    contractor = relationship("Contractor", back_populates="executors")
    stage = relationship("Stage", back_populates="executors")
    user = relationship("User", back_populates="executors")

