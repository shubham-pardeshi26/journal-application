# app/db/models/comment.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
# REMOVE THIS LINE: from sqlalchemy.dialects.postgresql import UUID # Not using PostgreSQL UUID for SQLite
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base
from app.db.models.user import get_utc_now

class Comment(Base):
    __tablename__ = "comments"

    # Changed from UUID(as_uuid=True) to String(36) and default lambda
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Changed from UUID(as_uuid=True) to String(36)
    journal_id = Column(String(36), ForeignKey('journals.id'), nullable=False)
    # Changed from UUID(as_uuid=True) to String(36)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    comment_text = Column(Text, nullable=True) # Nullable for media-only comments
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    journal = relationship("Journal", back_populates="comments")
    creator = relationship("User")
    media = relationship("Media", back_populates="comment_entry", cascade="all, delete-orphan") # Add cascade for media

    def __repr__(self):
        return f"<Comment(id='{self.id}', journal_id='{self.journal_id}')>"