# app/schemas/group.py

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
import uuid

# Forward declaration for Pydantic (needed for circular references)
class UserResponseMinimal(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    class Config:
        from_attributes = True

class GroupMemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    group_id: uuid.UUID
    joined_at: datetime
    is_admin: bool
    user: UserResponseMinimal # Nested user data
    class Config:
        from_attributes = True

class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    max_members: int = Field(..., ge=2, le=5) # Group size between 2 and 5

class GroupCreate(GroupBase):
    pass

class GroupResponse(GroupBase):
    id: uuid.UUID
    group_code: str
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    members: List[GroupMemberResponse] = [] # Nested list of members
    # You might want to add current_members_count
    class Config:
        from_attributes = True

class GroupJoin(BaseModel):
    group_code: str = Field(..., min_length=10, max_length=10) # Assuming 10 char unique code

class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)