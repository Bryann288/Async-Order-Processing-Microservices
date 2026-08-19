from sqlalchemy.ext.asyncio import AsyncSession
from src.models.order import Order, OrderItem, OrderStatus
from src.schemas.order import OrderCreate
import uuid

class OrderService:
    @staticmethod
    async def create_order(db: AsyncSession, user_id: uuid.UUID, data: OrderCreate) -> Order:
        total_amount = sum(item.quantity * item.unit_price for item in data.items)
        
        db_order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount
        )
        db.add(db_order)
        await db.flush()

        for item in data.items:
            db_item = OrderItem(
                order_id=db_order.id,
                product_code=item.product_code,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            db.add(db_item)

        await db.commit()
        await db.refresh(db_order)
        return db_order