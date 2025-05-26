# app/db/models/media.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
# REMOVE THIS LINE: from sqlalchemy.dialects.postgresql import UUID # Not using PostgreSQL UUID for SQLite
# REMOVE THIS LINE: from sqlalchemy.sql import func # Use get_utc_now instead
from sqlalchemy.orm import relationship
from app.db import Base
from app.db.models.user import get_utc_now # Import get_utc_now

class Media(Base):
    __tablename__ = "media"

    # Changed from UUID(as_uuid=True) to String(36) and default lambda
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Changed from UUID(as_uuid=True) to String(36)
    journal_id = Column(String(36), ForeignKey('journals.id'), nullable=True)
    # Changed from UUID(as_uuid=True) to String(36)
    comment_id = Column(String(36), ForeignKey('comments.id'), nullable=True)
    # ADDED: Uploader ID for consistency with User model
    uploader_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True) # Assuming media must have an uploader

    file_url = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False) # ENUM('image', 'video') - consider creating a Python Enum for this too
    caption = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, default=get_utc_now) # Changed from func.now() to get_utc_now
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)


    # Relationships
    journal_entry = relationship("Journal", foreign_keys=[journal_id], back_populates="media")
    comment_entry = relationship("Comment", foreign_keys=[comment_id], back_populates="media")
    uploader = relationship("User", back_populates="media") # Relationship to the User who uploaded

    def __repr__(self):
        return f"<Media(id='{self.id}', type='{self.file_type}')>"