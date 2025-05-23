# app/db/models/comment.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.models import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_id = Column(UUID(as_uuid=True), ForeignKey('journals.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    comment_text = Column(Text, nullable=True) # Nullable for media-only comments
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    journal = relationship("Journal", back_populates="comments")
    creator = relationship("User")
    media = relationship("Media", back_populates="comment_entry") # One-to-many relationship with media

    def __repr__(self):
        return f"<Comment(id='{self.id}', journal_id='{self.journal_id}')>"