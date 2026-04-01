
from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship

import bcrypt

from database.postgres_connection import Base
from enums.user_roles import UserRoles


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(150), unique=True, index=True)
    password_hash = Column(String(128))
    role = Column(Enum(UserRoles), nullable=False)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


    def __init__(self, username: str, email: str, password: str, role: UserRoles):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role

    def set_password(self, password):
        '''Hash the password and store it in the password_hash field'''
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        '''Check if the provided password matches the stored password hash'''
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))