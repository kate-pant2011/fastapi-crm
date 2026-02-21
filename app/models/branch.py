from .base import BaseModel
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

class Branch(BaseModel):
    __tablename__ = "branches"

    name = Column(String, unique=True, nullable=False)
    inn = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="branch")
    is_deleted = Column(Boolean, default=False, nullable=False)

    contractor_branches_link = relationship("ContractorBranch", back_populates="branch")
