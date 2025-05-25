# app/schemas/journal.py

from pydantic import BaseModel, Field, ConfigDict # Import ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum # Make sure Enum is imported

# Define the JournalType Enum (if you haven't already)
class JournalType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    GROUP = "group"

class JournalBase(BaseModel):
    # Add model_config for arbitrary types
    model_config = ConfigDict(arbitrary_types_allowed=True) # <--- ADD THIS LINE

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    journal_type: JournalType = Field(default=JournalType.PRIVATE) # Using your Enum
    # Assuming group_id is optional and only for GROUP journals
    group_id: Optional[uuid.UUID] = None # Using uuid.UUID for type hinting

class JournalCreate(JournalBase):
    pass

class JournalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    journal_type: Optional[JournalType] = None
    group_id: Optional[uuid.UUID] = None

class JournalResponse(JournalBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Use from_attributes for Pydantic v2