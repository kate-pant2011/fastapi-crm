from .base import BaseModel
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY


class Contractor(BaseModel):
    __tablename__ = "contractors"

    name = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(ARRAY(String(255)), nullable=True)
    description = Column(String(255), nullable=False)
    contractor_companies = Column(ARRAY(String(255)), nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)

    assignments = relationship("Assignment", back_populates="contractor")



