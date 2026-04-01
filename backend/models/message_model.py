from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime

from database.postgres_connection import Base


class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    content = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    
    conversation = relationship("Conversation", back_populates="messages")