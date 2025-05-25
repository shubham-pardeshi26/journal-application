# app/db/models/journal.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base
from app.db.models.user import get_utc_now
class Journal(Base):
    __tablename__ = "journals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'), nullable=True) # Nullable for solo journals
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    j_type = Column(String(50), nullable=True) # Will store ENUM values as string
    mood = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=get_utc_now) # <--- UPDATED
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now) # <--- UPDATED

    # Relationships
    creator = relationship("User", foreign_keys=[user_id])
    group = relationship("Group", foreign_keys=[group_id])
    comments = relationship("Comment", back_populates="journal")
    media = relationship("Media", back_populates="journal_entry")

    def __repr__(self):
        return f"<Journal(title='{self.title}', user_id='{self.user_id}')>"