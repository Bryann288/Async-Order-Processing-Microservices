from src.models.order import Order
from src.repositories.base import BaseRepository
from src.schemas.order import OrderCreate # Lo crearemos en la siguiente fase

class OrderRepository(BaseRepository[Order, OrderCreate]):
    # Aquí añadiremos métodos específicos como get_orders_by_user_id()
    pass

order_repo = OrderRepository(Order)