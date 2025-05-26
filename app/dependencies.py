# app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Annotated

from app.core.config import settings
from app.core.database import get_db
from app.db.models.user import User
from app.schemas.auth import TokenData # Ensure TokenData is imported

# OAuth2PasswordBearer defines the expected token location (header, query)
# and the URL for token issuance (which you'll implement for login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub") # 'sub' is the subject of the JWT
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.id).first()
    if user is None:
        raise credentials_exception
    
    # Optional: Check if user is active/verified if required for general access
    # if not user.is_active or not user.is_verified:
    #    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive or unverified user")

    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_current_active_verified_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    if not current_user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unverified email. Please verify your email to access this feature.")
    return current_user

# Add a dependency for admin users (optional for now, but good to plan)
# async def get_current_admin_user(
#     current_user: Annotated[User, Depends(get_current_active_verified_user)]
# ) -> User:
#     if not current_user.is_admin: # Assuming you'd add an `is_admin` field to User model
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
#     return current_user