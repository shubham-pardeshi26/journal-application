# app/services/user_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.db.models.user import User
from app.schemas.user import UserUpdate, UserPasswordChange, UserResponse
from app.services.auth_service import get_password_hash, verify_password # Import hashing functions

# Password hashing context (already defined in auth_service, but re-defining for completeness
# or if you prefer to keep this service more independent, though importing is cleaner)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Retrieves a user by their ID."""
    return db.query(User).filter(User.id == user_id).first()

async def update_user_profile(db: Session, user_id: str, user_update: UserUpdate) -> User:
    """Updates a user's profile information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True) # Pydantic v2: use model_dump
    
    # Handle username/email uniqueness if they are being updated
    if 'username' in update_data and update_data['username'] != user.username:
        existing_username = db.query(User).filter(User.username == update_data['username']).first()
        if existing_username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken.")
    
    if 'email' in update_data and update_data['email'] != user.email:
        existing_email = db.query(User).filter(User.email == update_data['email']).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken.")
        # If email changes, user needs to re-verify it
        user.is_verified = False # Reset verification status
        # In a real app, you'd also send a new verification email here
        # (similar to register_user, but we'll skip for now to keep focus)

    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

async def change_user_password(db: Session, user_id: str, password_change: UserPasswordChange) -> User:
    """Allows an authenticated user to change their password."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Verify current password
    if not verify_password(password_change.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password.")
    
    # Check if new password is same as old
    if verify_password(password_change.new_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be the same as the current password.")

    # Hash and update new password
    user.hashed_password = get_password_hash(password_change.new_password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Optional: async def deactivate_user(db: Session, user_id: str) -> User:
# Optional: async def delete_user(db: Session, user_id: str):