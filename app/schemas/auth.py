# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

# Schema for user login
class UserLogin(BaseModel):
    email_or_username: str
    password: str

# Schema for token response (after successful login)
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Schema for email verification request
class EmailVerificationRequest(BaseModel):
    email: EmailStr

# Schema for password forgot request
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# Schema for password reset request
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)
    confirm_new_password: str = Field(..., min_length=6)