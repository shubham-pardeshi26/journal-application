# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserLogin(BaseModel):
    username: str # This field will accept either username or email
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for data inside the JWT token (e.g., subject ID)."""
    id: Optional[str] = None # 'sub' field in JWT is typically string

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)
    confirm_new_password: str = Field(..., min_length=6)