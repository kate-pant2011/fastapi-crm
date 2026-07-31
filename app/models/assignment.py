from .base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship


class Assignment(BaseModel):
    __tablename__ = "assignments"

    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=False, index=True)

    deadline = Column(DateTime, nullable=False)

    contractor_id = Column(
        Integer, ForeignKey("contractors.id"), nullable=True, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    is_done = Column(Boolean, nullable=False, default=False)

    contractor = relationship("Contractor", back_populates="assignments")
    stage = relationship("Stage", back_populates="assignments")
    user = relationship("User", back_populates="assignments")
