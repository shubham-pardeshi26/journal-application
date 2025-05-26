# app/db/models/user.py

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, String, Boolean, DateTime
from sqlalchemy.sql import func # Keep func if you use it elsewhere, but get_utc_now is preferred for defaults
from sqlalchemy.orm import relationship # <-- Ensure this is imported
from app.db import Base

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
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # --- Ensure ALL of these relationships are present and correctly defined ---
    tokens = relationship("UserToken", back_populates="user", cascade="all, delete-orphan")
    journals = relationship("Journal", foreign_keys="[Journal.user_id]", back_populates="creator", cascade="all, delete-orphan")
    # This is the key relationship for groups a user OWNS/CREATES
    created_groups = relationship("Group", foreign_keys="[Group.created_by_user_id]", back_populates="creator") # <-- Crucial
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="creator", cascade="all, delete-orphan")
    media = relationship("Media", foreign_keys="[Media.uploader_id]", back_populates="uploader", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}')>"

class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    type = Column(String(50), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="tokens")

    def __repr__(self):
        return f"<UserToken(type='{self.type}', user_id='{self.user_id}')>"