from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from datetime import datetime

from database.postgres_connection import Base


class Metadata(Base):
    __tablename__ = "metadata"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String)
    source = Column(String)
    topic = Column(String)
    level = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    language = Column(String)