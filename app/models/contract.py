from .base import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

class ContractStatus(str, Enum):
    DRAFT = "draft"           
    PENDING = "pending"        
    SIGNED = "signed"          
    EXPIRED = "expired"       
    TERMINATED = "terminated" 

class Contract(BaseModel):
    __tablename__ = "contracts"

    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)
    company_id = Column(
        Integer, 
        ForeignKey("companies.id"), 
        nullable=False, 
        index=True
    )

    status = Column(
        SQLEnum(ContractStatus, name="contract_status_enum"), 
        nullable=False, 
        default=ContractStatus.DRAFT
    )

    description = Column(String, nullable=False)
    number = Column(String, nullable=False)
    name = Column(String, nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    branch = relationship("Branch", back_populates="client_contracts_link")
    company = relationship("Company", back_populates="contracts")
    projects = relationship("Project", back_populates="contract")

