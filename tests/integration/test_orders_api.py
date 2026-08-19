import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_create_order_unauthorized(client: AsyncClient):
    payload = {
        "items": [
            {"product_code": "SKU-001", "quantity": 1, "unit_price": 50.0}
        ]
    }
    response = await client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_order_authenticated(client: AsyncClient, auth_headers: dict):
    payload = {
        "items": [
            {"product_code": "SKU-001", "quantity": 3, "unit_price": 10.50},
            {"product_code": "SKU-002", "quantity": 1, "unit_price": 20.00}
        ]
    }
    response = await client.post("/api/v1/orders/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["status"] == "PENDING"
    assert data["total_amount"] == 51.50