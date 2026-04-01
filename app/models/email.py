from .base import BaseModel
from sqlalchemy import Column, String, Integer, Boolean, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship

class Email(BaseModel):
    __tablename__ = "emails"
    server = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    login = Column(String(255), nullable=False, unique=True)
    password = Column(LargeBinary, nullable=False)
    personal = Column(Boolean, nullable=False, index=True)

    creator_id = Column(Integer, ForeignKey("users.id"), index=True, default=None)
    creator = relationship("User", back_populates="emails")

