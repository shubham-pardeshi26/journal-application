# app/schemas/media.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class MediaType(str):
    IMAGE = "image"
    VIDEO = "video"

class MediaBase(BaseModel):
    file_url: str
    file_type: MediaType
    caption: Optional[str] = Field(None, max_length=255)

class MediaUploadResponse(MediaBase):
    id: uuid.UUID
    journal_id: Optional[uuid.UUID]
    comment_id: Optional[uuid.UUID]
    uploaded_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

# For requests, when uploading, the file itself is handled by FastAPI's UploadFile,
# not typically within a Pydantic model for the multipart form.
# The `caption` could be part of the form data or a separate query parameter.