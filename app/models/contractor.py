from .base import BaseModel
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

class Contractor(BaseModel):
    __tablename__ = "contractors"
    
    name = Column(String)
    email = Column(String)
    description = Column(String)
    contractor_company = Column(String, default=None)
    contract = Column(String, default=None)
    is_deleted = Column(Boolean, default=False, nullable=False)

    assignments = relationship("Assignment", back_populates="contractor")

