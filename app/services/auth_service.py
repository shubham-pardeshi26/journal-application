# app/services/auth_service.py

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core import security
from app.core.config import settings
from app.db.models.user import User, UserToken
from app.schemas.user import UserCreate
from app.crud import user as crud_user # Import user CRUD operations
from app.services import email as email_service

async def register_user(db: Session, user_in: UserCreate, base_url: str) -> User:
    """Registers a new user, hashes password, and sends verification email."""
    # Check if user already exists
    existing_user = crud_user.get_user_by_email(db, email=user_in.email) or \
                    crud_user.get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )

    hashed_password = security.get_password_hash(user_in.password)
    user = crud_user.create_user(db, user_in=user_in, hashed_password=hashed_password)

    # Generate and send email verification token
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES)
    crud_user.create_user_token(
        db, user_id=user.id, token=token, token_type="email_verification", expires_at=expires_at
    )

    verification_url = f"{base_url}/api/v1/auth/verify-email?token={token}"
    await email_service.send_verification_email(user.email, user.username, verification_url)

    return user

async def authenticate_user(db: Session, email_or_username: str, password: str) -> Optional[User]:
    """Authenticates a user by email/username and password."""
    user = crud_user.get_user_by_email(db, email=email_or_username)
    if not user:
        user = crud_user.get_user_by_username(db, username=email_or_username)
    
    if not user or not security.verify_password(password, user.hashed_password):
        return None
    
    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your inbox for a verification link."
        )
    
    return user

async def generate_access_token(user: User) -> str:
    """Generates an access token for a given user."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return security.create_access_token(
        data={"sub": str(user.id), "email": user.email, "username": user.username},
        expires_delta=access_token_expires
    )

async def verify_user_email(db: Session, token: str) -> bool:
    """Verifies a user's email using a token."""
    user_token = crud_user.get_user_token_by_token_and_type(db, token=token, token_type="email_verification")

    if not user_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired token")
    
    if user_token.expires_at < datetime.now(timezone.utc):
        crud_user.delete_user_token(db, token_id=user_token.id) # Clean up expired token
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired")

    user = crud_user.get_user_by_id(db, user_id=user_token.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for this token")
    
    if user.is_verified:
        crud_user.delete_user_token(db, token_id=user_token.id) # Clean up used token
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

    crud_user.update_user_verified_status(db, user_id=user.id, is_verified=True)
    crud_user.delete_user_token(db, token_id=user_token.id) # Delete the used token
    return True

async def request_password_reset(db: Session, email: str, base_url: str) -> bool:
    """Initiates the password reset process by sending a reset email."""
    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        # For security, always return success even if email not found
        # to prevent enumeration attacks
        print(f"Password reset requested for non-existent email: {email}")
        return True

    # Delete any existing password reset tokens for this user
    crud_user.delete_user_tokens_by_type(db, user_id=user.id, token_type="password_reset")

    # Generate new token
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    crud_user.create_user_token(
        db, user_id=user.id, token=token, token_type="password_reset", expires_at=expires_at
    )

    reset_url = f"{base_url}/api/v1/auth/reset-password?token={token}"
    await email_service.send_password_reset_email(user.email, user.username, reset_url)
    return True

async def reset_user_password(db: Session, token: str, new_password: str) -> bool:
    """Resets user password using a token."""
    user_token = crud_user.get_user_token_by_token_and_type(db, token=token, token_type="password_reset")

    if not user_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired token")
    
    if user_token.expires_at < datetime.now(timezone.utc):
        crud_user.delete_user_token(db, token_id=user_token.id) # Clean up expired token
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired")

    user = crud_user.get_user_by_id(db, user_id=user_token.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for this token")
    
    hashed_password = security.get_password_hash(new_password)
    crud_user.update_user_password(db, user_id=user.id, hashed_password=hashed_password)
    crud_user.delete_user_token(db, token_id=user_token.id) # Delete the used token
    return True