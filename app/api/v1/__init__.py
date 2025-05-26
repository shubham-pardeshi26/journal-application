# app/api/v1/__init__.py

from fastapi import APIRouter

# Import your individual endpoint routers here
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router # <--- ADD THIS LINE
from app.api.v1.endpoints.group import router as groups_router


api_router = APIRouter()

# Include routers with their prefixes and tags
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(users_router, prefix="/users", tags=["Users"]) # <--- ADD THIS LINE
api_router.include_router(groups_router, prefix="/groups", tags=["Groups"])

# For future modules:
# from app.api.v1.endpoints.groups import router as groups_router

# from app.api.v1.endpoints.journals import router as journals_router
# api_router.include_router(journals_router, prefix="/journals", tags=["Journals"])