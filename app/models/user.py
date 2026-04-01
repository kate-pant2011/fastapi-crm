from .base import BaseModel, user_roles
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class User(BaseModel):
    __tablename__ = "users"

    branch_id = Column(Integer, ForeignKey("branches.id"), index=True)

    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, index=True)
    must_change_password = Column(Boolean, default=True)

    refresh_tokens = relationship("RefreshToken", back_populates="user")

    branch = relationship("Branch", back_populates="users")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    assignments = relationship("Assignment", back_populates="user")
    clients = relationship("Client", back_populates="manager")
    stage_templates = relationship("StageTemplate", back_populates="creator")
    files = relationship("File", back_populates="creator")
    emails = relationship("Email", back_populates="creator")
