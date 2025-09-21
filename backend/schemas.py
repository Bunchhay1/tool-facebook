# backend/schemas.py
from pydantic import BaseModel # CORRECTED: 'pantic' to 'pydantic'
from typing import Optional
from datetime import datetime

class AccountCreate(BaseModel):
    username: str
    password: str

class AccountResponse(BaseModel):
    id: int
    username: str
    status: str
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    content: str
    scheduled_at: Optional[datetime] = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    status: str
    class Config:
        from_attributes = True