from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from src.api.deps import get_db, oauth2_scheme
from src.middlewares.rate_limiter import rate_limiter
from src.schemas.order import OrderCreate, OrderResponse
from src.services.order_service import OrderService
from jose import jwt, JWTError
from src.core.config import settings

router = APIRouter(dependencies=[Depends(rate_limiter)])

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError()
        return uuid.UUID(user_id)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    return await OrderService.create_order(db=db, user_id=user_id, data=order_in)