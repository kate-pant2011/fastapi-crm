from .base import BaseModel
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship


class Branch(BaseModel):
    __tablename__ = "branches"

    name = Column(String, unique=True, nullable=False)
    inn = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="branch")
    is_archived = Column(Boolean, default=False, nullable=False)

    contractor_contracts_link = relationship(
        "ContractorContract", back_populates="branch"
    )
    client_contracts_link = relationship("Contract", back_populates="branch")
