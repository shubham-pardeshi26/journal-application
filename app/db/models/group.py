# app/db/models/group.py

from enum import Enum as pyEnum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum
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
    is_active = Column(Boolean, default=True)
    is_delete = Column(Boolean, default=False)

    # Relationships
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    # This is the crucial line: back_populates must match the relationship name in User
    creator = relationship("User", foreign_keys=[created_by_user_id], back_populates="created_groups") # <-- Crucial
    group_journals = relationship("Journal", back_populates="group", cascade="all, delete-orphan") # Add for journals belonging to group
    invitations = relationship("GroupMemberInvitation", back_populates="group")
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
    
class InvitationStatusEnum(pyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    EXPIRED = "expired"
    REJECTED = "rejected"

class GroupMemberInvitation(Base):
    __tablename__ = "group_member_invitations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invite_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36), ForeignKey('groups.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    status = Column(Enum(InvitationStatusEnum), default=InvitationStatusEnum.PENDING)
    create_date = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="invitations")
    user = relationship("User", back_populates="group_invitations")

    def __repr__(self):
        return f"<GroupMemberInvitation(invite_uuid='{self.invite_uuid}', group_id='{self.group_id}', user_id='{self.user_id}', status='{self.status}')>"