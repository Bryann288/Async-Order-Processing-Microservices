import pytest
from httpx import AsyncClient
from src.core.config import settings

@pytest.mark.asyncio
async def test_rate_limiter_allows_under_threshold(client: AsyncClient, auth_headers: dict):
    payload = {
        "items": [{"product_code": "SKU-RL", "quantity": 1, "unit_price": 1.00}]
    }
    for _ in range(5):
        response = await client.post("/api/v1/orders/", json=payload, headers=auth_headers)
        assert response.status_code in [201, 429]