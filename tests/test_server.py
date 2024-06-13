import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_index_route(test_client):
    response = await test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Master Server API"}
