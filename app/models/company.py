from .base import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Company(BaseModel):
    __tablename__ = "companies"

    client_id = Column(
        Integer, 
        ForeignKey("clients.id"), 
        nullable=False, 
        index=True
    )

    name = Column(String, nullable=False)
    inn = Column(String, nullable=False, unique=True)
    is_archived = Column(Boolean, default=False, nullable=False)

    client = relationship("Client", back_populates="companies")
    contracts = relationship("Contract", back_populates="company")