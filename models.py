from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base
import datetime

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    request_data = Column(String, index=True)
    response_data = Column(Text)  # Store JSON string of the response