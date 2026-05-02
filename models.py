from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base


class SpendEntry(Base):
    __tablename__ = "spend_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)