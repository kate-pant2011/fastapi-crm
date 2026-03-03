from .base import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship


class Client(BaseModel):
    __tablename__ = "clients"

    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    manager = relationship("User", back_populates="clients")

    name = Column(String, nullable=False)
    email = Column(ARRAY(String), nullable=True)
    telephone = Column(ARRAY(String), nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)

    projects = relationship("Project", back_populates="client")
    companies = relationship("Company", back_populates="client")
