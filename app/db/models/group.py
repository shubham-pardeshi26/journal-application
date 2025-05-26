# app/db/models/group.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Keep if used elsewhere
from app.db import Base
from app.db.models.user import get_utc_now # Ensure this is imported

class Group(Base):
    __tablename__ = "groups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True) # Assuming you have a description field
    group_code = Column(String(10), unique=True, index=True, nullable=False)
    max_members = Column(Integer, nullable=False)
    created_by_user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    # This is the crucial line: back_populates must match the relationship name in User
    creator = relationship("User", foreign_keys=[created_by_user_id], back_populates="created_groups") # <-- Crucial
    group_journals = relationship("Journal", back_populates="group", cascade="all, delete-orphan") # Add for journals belonging to group

    def __repr__(self):
        return f"<Group(name='{self.name}', code='{self.group_code}')>"

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36), ForeignKey('groups.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    joined_at = Column(DateTime, default=get_utc_now)
    is_admin = Column(Boolean, default=False)

    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships") # Ensure this matches User model

    def __repr__(self):
        return f"<GroupMember(group_id='{self.group_id}', user_id='{self.user_id}')>"