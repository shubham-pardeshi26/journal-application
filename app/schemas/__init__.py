# app/schemas/__init__.py

# app/schemas/__init__.py

from .user import UserCreate, UserResponse, UserUpdate, UserResponseMinimal
from .auth import UserLogin, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
from .group import GroupCreate, GroupResponse, GroupUpdate, GroupMemberResponse
from .journal import JournalCreate, JournalResponse, JournalUpdate # Ensure this is correct
from .comment import CommentCreate, CommentResponse, CommentUpdate
# from .media import MediaCreate, MediaResponse, MediaUpdate
# You might re-export specific models here for easier import