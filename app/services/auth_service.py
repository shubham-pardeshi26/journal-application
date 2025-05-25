# app/services/auth_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone # Ensure timezone is imported
from jose import jwt, JWTError
import uuid
import re

from app.core.config import settings
from app.db.models.user import User, UserToken
from app.schemas.user import UserCreate
# from app.schemas.auth import TokenData # If you commented this out previously, it's fine for this error

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

# --- JWT Token Generation ---
async def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def generate_access_token(user: User) -> str:
    """Generates an access token for a given user."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    return access_token

# --- User Authentication ---
async def authenticate_user(db: Session, username_or_email: str, password: str) -> User | None:
    """Authenticates a user by username/email and password."""
    user = db.query(User).filter((User.username == username_or_email) | (User.email == username_or_email)).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# --- User Registration ---
async def register_user(db: Session, user_in: UserCreate, base_url: str) -> User:
    """Registers a new user."""
    existing_user_username = db.query(User).filter(User.username == user_in.username).first()
    if existing_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    existing_user_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user_in.password)

    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    token_value = str(uuid.uuid4())
    # Use EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS here, not minutes, if that's what's in your settings
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES)
    
    db_token = UserToken(
        user_id=db_user.id,
        token=token_value,
        type="email_verification",
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    verification_link = f"{base_url}{settings.API_V1_STR}/auth/verify-email?token={token_value}"
    print(f"DEBUG: Email verification link for {db_user.email}: {verification_link}")
    return db_user

# --- Email Verification ---
async def verify_user_email(db: Session, token: str) -> bool:
    """Verifies user email using a token."""
    user_token = db.query(UserToken).filter(
        UserToken.token == token,
        UserToken.type == "email_verification"
    ).first()

    if not user_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification token not found or invalid.")

    # --- THE CRUCIAL FIX HERE ---
    # Make the retrieved expires_at timezone-aware (assuming it was stored as UTC)
    # This specifically addresses the TypeError for SQLite
    if user_token.expires_at.tzinfo is None: # Check if it's naive
        # If it's naive, assume it's UTC and make it aware
        aware_expires_at = user_token.expires_at.replace(tzinfo=timezone.utc)
    else:
        # If it's already aware, use it directly (or convert to UTC if needed, but here it implies UTC)
        aware_expires_at = user_token.expires_at


    if aware_expires_at < datetime.now(timezone.utc): # Now both are aware UTC
        db.delete(user_token)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token has expired.")

    user = db.query(User).filter(User.id == user_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User associated with token not found.")

    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified.")

    user.is_verified = True
    db.delete(user_token)
    db.commit()
    db.refresh(user)
    return True

# --- Password Reset ---
async def request_password_reset(db: Session, email: str, base_url: str):
    """Generates a password reset token and sends it to the user's email."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message": "If your email is registered, a password reset link has been sent."}

    db.query(UserToken).filter(
        UserToken.user_id == user.id,
        UserToken.type == "password_reset"
    ).delete()
    db.commit()

    token_value = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)

    db_token = UserToken(
        user_id=user.id,
        token=token_value,
        type="password_reset",
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    reset_link = f"{base_url}{settings.API_V1_STR}/auth/reset-password?token={token_value}"
    print(f"DEBUG: Password reset link for {user.email}: {reset_link}")
    return {"message": "If your email is registered, a password reset link has been sent."}


async def reset_user_password(db: Session, token: str, new_password: str):
    """Resets user password using a token."""
    user_token = db.query(UserToken).filter(
        UserToken.token == token,
        UserToken.type == "password_reset"
    ).first()

    if not user_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password reset token not found or invalid.")

    # --- THE CRUCIAL FIX HERE ---
    # Make the retrieved expires_at timezone-aware (assuming it was stored as UTC)
    if user_token.expires_at.tzinfo is None:
        aware_expires_at = user_token.expires_at.replace(tzinfo=timezone.utc)
    else:
        aware_expires_at = user_token.expires_at

    if aware_expires_at < datetime.now(timezone.utc): # Now both are aware UTC
        db.delete(user_token)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset token has expired.")

    user = db.query(User).filter(User.id == user_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User associated with token not found.")

    user.hashed_password = get_password_hash(new_password)
    db.delete(user_token)
    db.commit()
    db.refresh(user)