import pytest
import pytest_asyncio
import uuid
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.main import app
from src.core.config import settings
from src.api.deps import get_db
from src.core.security import create_access_token, get_password_hash
from src.models.user import User
from src.middlewares.rate_limiter import redis_client

# 1. NullPool previene conexiones huérfanas retenidas entre Event Loops cerrados
test_engine = create_async_engine(
    settings.async_database_url, 
    poolclass=NullPool,
    future=True
)
test_session_maker = async_sessionmaker(
    bind=test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_maker() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def cleanup_redis():
    """Limpia las claves de rate limit y resetea el pool de sockets entre tests."""
    yield
    try:
        await redis_client.flushdb()
        await redis_client.connection_pool.disconnect()
    except Exception:
        pass

@pytest_asyncio.fixture
async def test_user() -> AsyncGenerator[User, None]:
    """Crea y persiste un usuario real para cumplir con la integridad referencial (FK)."""
    async with test_session_maker() as session:
        user = User(
            id=uuid.uuid4(),
            email=f"test_{uuid.uuid4().hex[:6]}@empresa.com",
            hashed_password=get_password_hash("TestPass123!"),
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        yield user

@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Genera cabecera JWT válida vinculada al usuario persistido."""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP ASGI asíncrono."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac