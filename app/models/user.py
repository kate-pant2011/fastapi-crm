from .base import BaseModel, user_roles
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class User(BaseModel):
    __tablename__ = "users"

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    position = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    
    is_active = Column(Boolean, default=False)

    refresh_tokens =  relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    company = relationship("Company", back_populates="users")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    executors = relationship("Executor", back_populates="user")
    clients = relationship("Client", back_populates="manager")

