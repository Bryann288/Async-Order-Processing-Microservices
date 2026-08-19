from pydantic import BaseModel, ConfigDict
from typing import List
import uuid
from datetime import datetime
from src.models.order import OrderStatus

class OrderItemCreate(BaseModel):
    product_code: str
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: OrderStatus
    total_amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)