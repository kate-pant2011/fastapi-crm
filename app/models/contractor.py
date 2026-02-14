from datetime import datetime
from .base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

class Contractor(BaseModel):
    __tablename__ = "contractors"
    
    name = Column(String)
    email = Column(String)
    description = Column(String)
    contractor_company = Column(String, default=None)
    contract = Column(String, default=None)

    executors = relationship("Executor", back_populates="contractor")

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    company = relationship("Company", back_populates="contractors")