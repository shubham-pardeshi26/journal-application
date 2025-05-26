# app/schemas/journal.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
# Import the JournalType Enum from your models
from app.db.models.journal import JournalType # <--- IMPORTANT

class JournalBase(BaseModel):
    title: Optional[str] = None
    content: str
    location: Optional[str] = None
    j_type: JournalType = JournalType.PRIVATE # Use the Enum directly with a default
    mood: Optional[str] = None
    group_id: Optional[str] = None # Will be str for UUIDs

class JournalCreate(JournalBase):
    pass # No additional fields for creation beyond base

class JournalUpdate(JournalBase):
    content: Optional[str] = None # Make content optional for update
    j_type: Optional[JournalType] = None # Make type optional for update
    # group_id etc. can be updated too if allowed

class JournalResponse(JournalBase):
    id: str # Change to str
    user_id: str # Change to str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True