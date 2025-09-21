# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    encrypted_password = Column(String, nullable=False)
    status = Column(String, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Inside backend/models.py
# ... (Account class remains the same) ...

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    status = Column(String, default='pending')
    scheduled_at = Column(DateTime(timezone=True), nullable=True) # Allow null for immediate posts
    created_at = Column(DateTime(timezone=True), server_default=func.now())