from .base import BaseModel
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    jti = Column(String, unique=True, nullable=False)
    device = Column(String, nullable=False)

    is_active = Column(Boolean, nullable=False)

    exp = Column(DateTime(timezone=True), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="refresh_tokens")
