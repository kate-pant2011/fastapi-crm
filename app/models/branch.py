from .base import BaseModel
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship


class Branch(BaseModel):
    __tablename__ = "branches"

    name = Column(String(255), unique=True, nullable=False)
    inn = Column(String(255), unique=True, nullable=False, index=True)

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

    users = relationship("User", back_populates="branch")
    is_archived = Column(Boolean, default=False, nullable=False, index=True)

    stamp_file_id = Column(Integer, ForeignKey("files.id", ondelete="SET NULL"))
    stamp_file = relationship("File")
    stamp_width_mm = Column(Integer, default=100)

    client_contracts_link = relationship("Contract", back_populates="branch")
