from .base import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Company(BaseModel):
    __tablename__ = "companies"

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    inn = Column(String(12), nullable=False, unique=True, index=True)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)

    kpp = Column(String(255), nullable=True)
    ogrn = Column(String(255), nullable=True)
    okpo = Column(String(255), nullable=True)
    okved = Column(String(255), nullable=True)
    okfs = Column(String(255), nullable=True)
    okopf = Column(String(255), nullable=True)
    okato = Column(String(255), nullable=True)

    legal_address = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)

    email = Column(String(255), nullable=True)
    telephone = Column(String(40), nullable=True)
    website = Column(String(255), nullable=True)

    director_full_name = Column(String(255), nullable=True)
    director_short_name = Column(String(255), nullable=True)
    director_position = Column(String(255), nullable=True)
    authority_document = Column(String(255), nullable=True)

    bank_name = Column(String(255), nullable=True)
    bik = Column(String(255), nullable=True)
    checking_account = Column(String(255), nullable=True)   
    correspondent_account = Column(String(255), nullable=True)

    client = relationship("Client", back_populates="companies")
    contracts = relationship("Contract", back_populates="company")
