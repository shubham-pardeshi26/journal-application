# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import api_router as v1_api_router # Correctly imports the 'api_router' from app.api.v1
# from app.core.database import Base, engine # Keep this line if you want the startup_event for create_all, otherwise remove

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include the API routers
app.include_router(v1_api_router, prefix=settings.API_V1_STR)

# Optional: Create database tables on startup if not using Alembic for initial setup
# Since you've successfully run Alembic, you should keep this commented out
# @app.on_event("startup")
# async def startup_event():
#     # Base.metadata.create_all(bind=engine)
#     print("FastAPI application started and ready.")


@app.get("/")
async def root():
    return {"message": "Welcome to the Journaling App API. Visit /docs for API documentation."}

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}