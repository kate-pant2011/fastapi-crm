from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True 
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)



