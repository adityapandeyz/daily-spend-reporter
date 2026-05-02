from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class SpendEntry(Base):
    __tablename__ = "spend_entries"
    
    # We define columns here!
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, primary_key=False, index=False)
    category = Column(String, primary_key=False, index=False)
    description = Column(String, primary_key=False, index=False)
    created_at = Column(DateTime, primary_key=False, index=False, default=datetime.now)

   