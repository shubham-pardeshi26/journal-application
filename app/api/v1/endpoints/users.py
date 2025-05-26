# app/api/v1/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.database import get_db
from app.schemas.user import UserResponse, UserUpdate, UserPasswordChange
from app.services import user_service
from app.dependencies import get_current_active_user, get_current_active_verified_user

router = APIRouter()

@router.get("/me", response_model=UserResponse, summary="Get current user's profile")
async def read_current_user(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    """
    Get the profile information of the currently authenticated user.
    Requires an active user.
    """
    return current_user # get_current_active_user already returns a User object from DB, Pydantic converts it

@router.put("/me", response_model=UserResponse, summary="Update current user's profile")
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Update the profile information of the currently authenticated user.
    Requires an active user.
    """
    updated_user = await user_service.update_user_profile(db, str(current_user.id), user_update)
    return updated_user

@router.put("/me/password", status_code=status.HTTP_200_OK, summary="Change current user's password")
async def change_current_user_password(
    password_change: UserPasswordChange,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Allow the currently authenticated user to change their password.
    Requires an active user.
    """
    if password_change.new_password != password_change.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm new password do not match."
        )
    
    await user_service.change_user_password(db, str(current_user.id), password_change)
    return {"message": "Password changed successfully."}

# Optional: Get user by ID (e.g., for admin or public profiles later)
# @router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID (for admin/public profiles)")
# async def read_user_by_id(
#     user_id: str,
#     db: Session = Depends(get_db),
#     # This might require an admin user or specific public profile logic
#     # current_user: Annotated[UserResponse, Depends(get_current_admin_user)] # Example for admin
# ):
#     user = await user_service.get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     return user