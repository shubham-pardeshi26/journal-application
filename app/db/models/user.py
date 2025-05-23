# app/db/models/user.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID # Use UUID for PostgreSQL, or String for SQLite/MySQL UUID representation
from sqlalchemy.sql import func
from app.db.models import Base # Import Base from the package's __init__.py, or adjust import if Base is only in database.py

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(email='{self.email}')>"

class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False) # Foreign Key relationship can be added later or managed at CRUD level
    token = Column(String(255), unique=True, index=True, nullable=False)
    type = Column(String(50), nullable=False) # ENUM('email_verification', 'password_reset')
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<UserToken(type='{self.type}', user_id='{self.user_id}')>"