from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from .database import Base

class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    casual_response = Column(Text, nullable=False)
    formal_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)