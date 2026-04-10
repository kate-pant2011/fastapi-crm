from .base import BaseModel
from sqlalchemy import Column, String, Integer, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship


class Email(BaseModel):
    __tablename__ = "emails"
    server = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    login = Column(String(255), nullable=False, unique=True)
    password = Column(LargeBinary, nullable=False)

    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, default=None)
    creator = relationship("User", back_populates="creator_emails", foreign_keys=[creator_id])
    owner = relationship("User", back_populates="owner_emails", foreign_keys=[owner_id])









