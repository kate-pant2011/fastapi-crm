from .base import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Client(BaseModel):
    __tablename__ = "clients"

    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    manager = relationship("User", back_populates="clients")

    name = Column(String)
    company_name = Column(String, nullable=True)
    inn = Column(Integer, nullable=True)
    email = Column(String, nullable=True)
    telephone = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    projects = relationship("Project", back_populates="client")