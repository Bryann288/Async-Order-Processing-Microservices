import asyncio
from src.core.database import async_session_maker
from src.models.user import User
from src.core.security import get_password_hash

async def seed_user():
    async with async_session_maker() as session:
        admin = User(
            email="admin@empresa.com",
            hashed_password=get_password_hash("SuperSecret123!")
        )
        session.add(admin)
        await session.commit()
        print("✅ Usuario de prueba inyectado correctamente en PostgreSQL.")

if __name__ == "__main__":
    asyncio.run(seed_user())
    