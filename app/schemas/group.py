# app/schemas/group.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
# REMOVE: import uuid # No longer needed for str types
from app.schemas.user import UserResponseMinimal # <--- IMPORT UserResponseMinimal here

# Removed direct definition of UserResponseMinimal as it's now imported

class GroupMemberResponse(BaseModel):
    id: str # Change from uuid.UUID to str
    user_id: str # Change from uuid.UUID to str
    group_id: str # Change from uuid.UUID to str
    joined_at: datetime
    is_admin: bool
    user: UserResponseMinimal # Nested user data, now correctly typed as str for IDs
    class Config:
        from_attributes = True

class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    max_members: int = Field(..., ge=2, le=5) # Group size between 2 and 5
    # Add group_code to GroupBase for consistency with GroupCreate/Update
    group_code: Optional[str] = Field(None, min_length=8, max_length=10) # Made optional for auto-generation
    description : Optional[str] = None

class GroupCreate(GroupBase):
    pass # No additional fields for creation beyond base

class GroupResponse(GroupBase):
    id: str # Change from uuid.UUID to str
    # group_code is now in GroupBase
    created_by_user_id: str # Change from uuid.UUID to str
    created_at: datetime
    updated_at: datetime
    members: List[GroupMemberResponse] = [] # Nested list of members
    # You might want to add current_members_count
    class Config:
        from_attributes = True

class GroupJoin(BaseModel):
    group_code: str = Field(..., min_length=8, max_length=10) # Assuming 8-10 char code

class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    group_code: Optional[str] = Field(None, min_length=8, max_length=10) # Added group_code update
    max_members: Optional[int] = Field(None, ge=2, le=5) # Added max_members update


class GroupMemberAdd(BaseModel):
    user_id: str # The ID of the user to add