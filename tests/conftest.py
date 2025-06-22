# # tests/conftest.py

# import pytest
# from httpx import AsyncClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import StaticPool # Important for SQLite in-memory tests

# from app.core.database import get_db
# from app.db import Base # Your Base declarative model
# from app.main import app # Your FastAPI application instance
# from app.db.models.user import User # Import User model for test data
# from app.core.security import create_access_token, get_password_hash # For creating test users

# # --- DATABASE FIXTURES ---

# # Use an in-memory SQLite database for tests
# # For production/staging, you'd use a real database, but for tests, in-memory is fast and isolated.
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# # Create a test engine and session
# # StaticPool is important for in-memory SQLite with multiple threads/sessions
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# @pytest.fixture(name="db_session", scope="function")
# def db_session_fixture():
#     """
#     Creates a new database session for each test, with all tables created
#     and then dropped after the test completes.
#     """
#     Base.metadata.create_all(bind=engine) # Create tables
#     connection = engine.connect()
#     transaction = connection.begin()
#     session = TestingSessionLocal(bind=connection)

#     # Override the default get_db dependency for tests
#     app.dependency_overrides[get_db] = lambda: session

#     try:
#         yield session
#     finally:
#         session.close()
#         transaction.rollback() # Rollback the transaction to clear changes
#         connection.close()
#         Base.metadata.drop_all(bind=engine) # Drop tables


# # --- APP CLIENT FIXTURES ---

# @pytest.fixture(name="client", scope="function")
# async def client_fixture(db_session):
#     """
#     Provides an asynchronous test client for the FastAPI application.
#     This client will use the isolated test database session.
#     """
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         yield ac

# # --- AUTHENTICATION FIXTURES ---

# @pytest.fixture(name="test_user_password")
# def test_user_password_fixture():
#     """Returns a simple password for test users."""
#     return "testpassword"

# @pytest.fixture(name="test_user")
# def test_user_fixture(db_session, test_user_password) -> User:
#     """
#     Creates a test user in the database for authenticated test cases.
#     """
#     user_email = "test@example.com"
#     user = db_session.query(User).filter(User.email == user_email).first()
#     if not user:
#         hashed_password = get_password_hash(test_user_password)
#         user = User(
#             username="testuser",
#             email=user_email,
#             hashed_password=hashed_password,
#             is_active=True,
#             is_verified=True,
#             full_name="Test User"
#         )
#         db_session.add(user)
#         db_session.commit()
#         db_session.refresh(user)
#     return user

# @pytest.fixture(name="admin_user")
# def admin_user_fixture(db_session, test_user_password) -> User:
#     """
#     Creates an admin test user for test cases requiring admin privileges.
#     """
#     admin_email = "admin@example.com"
#     admin = db_session.query(User).filter(User.email == admin_email).first()
#     if not admin:
#         hashed_password = get_password_hash(test_user_password)
#         admin = User(
#             username="adminuser",
#             email=admin_email,
#             hashed_password=hashed_password,
#             is_active=True,
#             is_verified=True,
#             full_name="Admin User"
#         )
#         db_session.add(admin)
#         db_session.commit()
#         db_session.refresh(admin)
#     return admin


# @pytest.fixture(name="test_user_token")
# def test_user_token_fixture(test_user: User) -> str:
#     """
#     Generates an access token for the test_user.
#     """
#     # Adjust token expiration time for tests if necessary
#     return create_access_token(data={"sub": test_user.email})

# @pytest.fixture(name="admin_user_token")
# def admin_user_token_fixture(admin_user: User) -> str:
#     """
#     Generates an access token for the admin_user.
#     """
#     return create_access_token(data={"sub": admin_user.email})
