# app/api/v1/endpoints/auth.py (No changes needed here based on previous content)

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.database import get_db
from app.core.config import settings
from app.schemas.auth import UserLogin, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service

router = APIRouter() # This 'router' object is what we're importing in __init__.py

# ... (rest of your auth.py content) ...

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    request: Request, # To get base URL for verification link
    db: Session = Depends(get_db)
):
    """
    Registers a new user and sends an email verification link.
    """
    base_url = str(request.base_url).rstrip('/')
    user = await auth_service.register_user(db, user_in, base_url)
    return user

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], # Standard form for login
    db: Session = Depends(get_db)
):
    """
    Authenticates a user and returns JWT access token.
    Uses OAuth2PasswordRequestForm for compatibility with standard client flows.
    """
    user = await auth_service.authenticate_user(db, form_data.username, form_data.password) # form_data.username can be email or username
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = await auth_service.generate_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-email", summary="Verify user email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verifies user's email using the provided token.
    """
    success = await auth_service.verify_user_email(db, token)
    if success:
        return {"message": "Email verified successfully!"}
    # auth_service.verify_user_email already raises HTTPException on failure
    return {"message": "Failed to verify email."} # Fallback, should not be reached


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    request: Request, # To get base URL for reset link
    db: Session = Depends(get_db)
):
    """
    Initiates password reset process by sending a reset link to the user's email.
    """
    base_url = str(request.base_url).rstrip('/')
    await auth_service.request_password_reset(db, request_data.email, base_url)
    # Always return success to prevent email enumeration
    return {"message": "If your email is registered, a password reset link has been sent."}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Resets user password using the provided token and new password.
    """
    if request_data.new_password != request_data.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match"
        )
    
    await auth_service.reset_user_password(db, request_data.token, request_data.new_password)
    return {"message": "Password has been reset successfully."}