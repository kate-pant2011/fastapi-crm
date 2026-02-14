from .base import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String,DateTime
from sqlalchemy.orm import relationship

class Company(BaseModel):
    __tablename__ = "companies"

    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=True)
    inn = Column(Integer, unique=True, nullable=True)
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    contractors = relationship("Contractor", back_populates="company")
