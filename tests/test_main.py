# tests/test_main.py

import pytest
from httpx import AsyncClient # Correct import for AsyncClient

@pytest.mark.asyncio
async def test_read_root(client: AsyncClient): # <-- Change 'requests' to 'AsyncClient'
    """
    Tests the root endpoint of the FastAPI application.
    Uses the 'client' fixture provided by conftest.py.
    """
    response = await client.get("/")
    assert response.status_code == 200
    # Also, ensure the expected message matches your app.main.py exactly
    assert response.json() == {"message": "Welcome to the Journaling App API. Visit /docs for API documentation."}
    # (Note: Your traceback shows "Welcome to the Journaling App API. Visit /docs for API documentation.",
    # ensure this assertion matches what your app.main.py actually returns.)