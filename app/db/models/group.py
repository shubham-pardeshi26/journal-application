# app/db/models/group.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.models import Base

class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    group_code = Column(String(10), unique=True, index=True, nullable=False)
    max_members = Column(Integer, nullable=False)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    members = relationship("GroupMember", back_populates="group")
    creator = relationship("User", foreign_keys=[created_by_user_id]) # Assuming User model is defined

    def __repr__(self):
        return f"<Group(name='{self.name}', code='{self.group_code}')>"

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    joined_at = Column(DateTime, default=func.now())
    is_admin = Column(Boolean, default=False)

    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User") # Assuming User model is defined

    def __repr__(self):
        return f"<GroupMember(group_id='{self.group_id}', user_id='{self.user_id}')>"