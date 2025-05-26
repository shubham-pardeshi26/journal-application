# app/db/models/journal.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum # Import Enum
# REMOVE THIS LINE: from sqlalchemy.dialects.postgresql import UUID # Not using PostgreSQL UUID for SQLite
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base
from app.db.models.user import get_utc_now

# Define JournalType Enum directly in this file or import if already defined globally
import enum
class JournalType(enum.Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    GROUP = "GROUP"

class Journal(Base):
    __tablename__ = "journals"

    # Changed from UUID(as_uuid=True) to String(36) and default lambda
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Changed from UUID(as_uuid=True) to String(36)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    # Changed from UUID(as_uuid=True) to String(36)
    group_id = Column(String(36), ForeignKey('groups.id'), nullable=True) # Nullable for solo journals
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    # Changed to use Enum type directly
    j_type = Column(Enum(JournalType), default=JournalType.PRIVATE, nullable=False)
    mood = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    creator = relationship("User", foreign_keys=[user_id], back_populates="journals") # Add back_populates
    group = relationship("Group", foreign_keys=[group_id], back_populates="group_journals") # Add back_populates
    comments = relationship("Comment", back_populates="journal", cascade="all, delete-orphan") # Add cascade
    media = relationship("Media", back_populates="journal_entry", cascade="all, delete-orphan") # Add cascade

    def __repr__(self):
        return f"<Journal(title='{self.title}', user_id='{self.user_id}')>"