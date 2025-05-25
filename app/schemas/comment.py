# app/schemas/comment.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# Forward declaration for Pydantic
class MediaResponseMinimal(BaseModel):
    id: uuid.UUID
    file_url: str
    file_type: str
    caption: Optional[str]
    uploaded_at: datetime
    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    comment_text: Optional[str] = Field(None, max_length=1000)

class CommentCreate(CommentBase):
    # For file uploads, it's typically handled via FastAPI's File/UploadFile directly
    # and not part of the Pydantic model for the request body for multipart/form-data.
    # The API endpoint will accept both text and file.
    pass

class CommentUpdate(BaseModel):
    comment_text: Optional[str] = Field(None, max_length=1000)

class CommentResponse(CommentBase):
    id: uuid.UUID
    journal_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    media: List[MediaResponseMinimal] = [] # Nested list of media for the comment

    class Config:
        from_attributes = True