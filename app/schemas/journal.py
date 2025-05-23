# app/schemas/journal.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class JournalType(str): # Define custom type or just use str for enum
    MEMORY = "memory"
    SPECIAL_DAY = "special_day"
    REFLECTION = "reflection"
    GRATITUDE = "gratitude"
    GOAL = "goal"
    DREAM = "dream"
    OTHER = "other"

class JournalBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: str
    location: Optional[str] = Field(None, max_length=255)
    j_type: Optional[JournalType] = None # Use the custom type
    mood: Optional[str] = Field(None, max_length=50)

class JournalCreate(JournalBase):
    group_id: Optional[uuid.UUID] = None # Nullable for solo journals

class JournalUpdate(JournalBase):
    pass # All fields are optional for update

# Forward declaration for Pydantic (to prevent circular imports)
class CommentResponseMinimal(BaseModel):
    id: uuid.UUID
    comment_text: Optional[str]
    user_id: uuid.UUID
    created_at: datetime
    class Config:
        from_attributes = True

class MediaResponseMinimal(BaseModel):
    id: uuid.UUID
    file_url: str
    file_type: str
    caption: Optional[str]
    uploaded_at: datetime
    class Config:
        from_attributes = True


class JournalResponse(JournalBase):
    id: uuid.UUID
    user_id: uuid.UUID
    group_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    comments: List[CommentResponseMinimal] = [] # Optional: include comments or fetch separately
    media: List[MediaResponseMinimal] = [] # Optional: include media or fetch separately

    class Config:
        from_attributes = True