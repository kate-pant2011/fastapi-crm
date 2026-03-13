from .base import BaseModel
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship


class Branch(BaseModel):
    __tablename__ = "branches"

    name = Column(String(255), unique=True, nullable=False)
    inn = Column(String(255), unique=True, nullable=False, index=True)
    users = relationship("User", back_populates="branch")
    is_archived = Column(Boolean, default=False, nullable=False, index=True)

    client_contracts_link = relationship("Contract", back_populates="branch")
