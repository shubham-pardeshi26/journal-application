# app/db/models/group.py
# ...
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
import uuid # Make sure uuid is imported
from app.db.models.user import get_utc_now
class Group(Base):
    __tablename__ = "groups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    group_code = Column(String(10), unique=True, index=True, nullable=False)
    max_members = Column(Integer, nullable=False)
    # CORRECTED LINE: Removed type_=String(36) from ForeignKey
    created_by_user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=get_utc_now) # <--- UPDATED
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now) # <--- UPDATED

    # Relationships
    members = relationship("GroupMember", back_populates="group")
    creator = relationship("User", foreign_keys=[created_by_user_id]) # Still need foreign_keys here for clarity/ambiguity if multiple FKs to User

    def __repr__(self):
        return f"<Group(name='{self.name}', code='{self.group_code}')>"

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # CORRECTED LINE: Removed type_=String(36) from ForeignKey
    group_id = Column(String(36), ForeignKey('groups.id'), nullable=False)
    # CORRECTED LINE: Removed type_=String(36) from ForeignKey
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    joined_at = Column(DateTime, default=get_utc_now)
    is_admin = Column(Boolean, default=False)

    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User")

    def __repr__(self):
        return f"<GroupMember(group_id='{self.group_id}', user_id='{self.user_id}')>"