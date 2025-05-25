# app/api/v1/__init__.py

from fastapi import APIRouter

# Corrected Import: Import the 'router' object directly from the endpoints module
from app.api.v1.endpoints.auth import router as auth_router # Alias it to avoid name collision if you have multiple routers

# from app.api.v1.endpoints.users import router as users_router # For future
# from app.api.v1.endpoints.groups import router as groups_router # For future
# from app.api.v1.endpoints.journals import router as journals_router # For future
# from app.api.v1.endpoints.comments import router as comments_router # For future
# from app.api.v1.endpoints.media import router as media_router # For future


api_router = APIRouter()

# Include routers with their prefixes and tags
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
# api_router.include_router(users_router, prefix="/users", tags=["Users"]) # For future
# api_router.include_router(groups_router, prefix="/groups", tags=["Groups"]) # For future
# api_router.include_router(journals_router, prefix="/journals", tags=["Journals"]) # For future
# api_router.include_router(comments_router, prefix="/comments", tags=["Comments"]) # For future
# api_router.include_router(media_router, prefix="/media", tags=["Media"]) # For future