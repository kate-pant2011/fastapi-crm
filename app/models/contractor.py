from .base import BaseModel
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY


class Contractor(BaseModel):
    __tablename__ = "contractors"

    name = Column(String, unique=True, nullable=False)
    email = Column(ARRAY(String), nullable=True)
    description = Column(String, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    assignments = relationship("Assignment", back_populates="contractor")

    contracts = relationship("ContractorContract", back_populates="contractor")


class ContractorContract(BaseModel):
    __tablename__ = "contractor_contracts"

    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)
    contractor_id = Column(
        Integer, ForeignKey("contractors.id"), nullable=False, index=True
    )

    description = Column(String, nullable=True)

    contractor_company = Column(String, nullable=True)
    contractor_inn = Column(String, nullable=True)
    contract_number = Column(String, nullable=True)
    contract_name = Column(String, nullable=True)
    contract_exp = Column(DateTime, nullable=True)

    is_archived = Column(Boolean, default=False, nullable=False)

    branch = relationship("Branch", back_populates="contractor_contracts_link")
    contractor = relationship("Contractor", back_populates="contracts")
