from .base import BaseModel
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import relationship


class PasswordResetToken(BaseModel):
    __tablename__ = "reset_tokens"

    jti = Column(String, unique=True, nullable=False)
    device = Column(String, nullable=False)

    used_at = Column(DateTime(timezone=True), nullable=True)

    exp = Column(DateTime(timezone=True), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="reset_tokens")