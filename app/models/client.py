from .base import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Client(BaseModel):
    __tablename__ = "clients"

    manager_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    manager = relationship("User", back_populates="clients")

    name = Column(String)
    company_name = Column(String, nullable=True)
    inn = Column(Integer, nullable=True)
    email = Column(String, nullable=True)
    telephone = Column(Integer, nullable=True)

    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")