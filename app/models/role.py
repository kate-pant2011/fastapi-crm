from .base import BaseModel, user_roles
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, nullable=False, unique=True)

    users = relationship("User", secondary=user_roles, back_populates="roles")
