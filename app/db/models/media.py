# app/db/models/media.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.models import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_id = Column(UUID(as_uuid=True), ForeignKey('journals.id'), nullable=True)
    comment_id = Column(UUID(as_uuid=True), ForeignKey('comments.id'), nullable=True)
    file_url = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False) # ENUM('image', 'video')
    caption = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, default=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    journal_entry = relationship("Journal", foreign_keys=[journal_id], back_populates="media")
    comment_entry = relationship("Comment", foreign_keys=[comment_id], back_populates="media")

    def __repr__(self):
        return f"<Media(id='{self.id}', type='{self.file_type}')>"