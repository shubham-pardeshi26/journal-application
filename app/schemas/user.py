# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid

# Base User schema for common attributes
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

# Schema for creating a new user (registration)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

# Schema for user data returned from API (sensitive fields omitted)
class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Pydantic v2.0+ uses from_attributes instead of orm_mode

# Schema for updating a user's profile
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None