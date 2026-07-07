from .base import BaseModel
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship


class Branch(BaseModel):
    __tablename__ = "branches"

    name = Column(String(255), unique=True, nullable=False)
    inn = Column(String(255), unique=True, nullable=False, index=True)
    #kpp = Column(String(255), unique=True, nullable=True)
    #ogrn = Column(String(255), unique=True, nullable=True)

    #legal_adress = Column(String(255), unique=True, nullable=True)
    #adress = Column(String(255), unique=True, nullable=True)

    users = relationship("User", back_populates="branch")
    is_archived = Column(Boolean, default=False, nullable=False, index=True)

    stamp_file_id = Column(Integer, ForeignKey("files.id"))
    stamp_file = relationship("File")
    stamp_is_public = Column(Boolean, default=True) # Needs to be removed
    stamp_width_mm = Column(Integer, default=100)

    client_contracts_link = relationship("Contract", back_populates="branch")
