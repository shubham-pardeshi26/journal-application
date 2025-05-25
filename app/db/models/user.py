# app/db/models/user.py

import uuid
from datetime import datetime, timezone # Import timezone
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db import Base

# Define a function to get UTC now
def get_utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    # Use get_utc_now for default values
    created_at = Column(DateTime, default=get_utc_now) # <--- UPDATED
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now) # <--- UPDATED

    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}')>"

class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    type = Column(String(50), nullable=False)
    expires_at = Column(DateTime, nullable=False) # <--- THIS IS THE ONE THAT WAS FAILING
    created_at = Column(DateTime, default=get_utc_now) # <--- UPDATED

    def __repr__(self):
        return f"<UserToken(type='{self.type}', user_id='{self.user_id}')>"