# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid

# Base User schema for common attributes
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100) # <--- ADDED HERE

# Schema for creating a new user (registration)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# Schema for user data returned from API (sensitive fields omitted)
class UserResponse(UserBase): # <--- Inherits full_name from UserBase
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema for updating a user's profile
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100) # <--- ADDED HERE

# Also update the UserResponseMinimal for Group schema if you copied it into app/schemas/group.py
# (This is just a reminder, if it's in a separate file, you'd update it there)
# If UserResponseMinimal is used in other schemas (e.g., in Group schema), make sure it also includes full_name if desired for minimal representation.
# For example:
class UserResponseMinimal(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    full_name: Optional[str] = None # <--- ADDED HERE IF YOU NEED IT FOR MINIMAL
    class Config:
        from_attributes = True