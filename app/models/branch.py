from .base import BaseModel
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

class Branch(BaseModel):
    __tablename__ = "branches"

    name = Column(String, unique=True, nullable=False)
    main_branch = Column(Boolean, default=False, nullable=False)
    inn = Column(Integer, unique=True, nullable=True)
    users = relationship("User", back_populates="branch")
    is_deleted = Column(Boolean, default=False, nullable=False)
