from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from datetime import datetime
from .database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    eventId = Column(String, unique=True, index=True)

    type = Column(String)
    tenantId = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String)

    metadata_ = Column("metadata",JSON, nullable=True)

    occurredAt = Column(DateTime, nullable=True)
    traceId = Column(String)

    storedAt = Column(DateTime, default=datetime.utcnow)