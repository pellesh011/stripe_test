from payments.domain.entities.order import Order
from payments.domain.repositories.order import OrderRepository


class GetOrdersUseCase:
    def __init__(
        self,
        orders: OrderRepository,
    ):
        self.orders = orders

    def execute(self) -> list[Order]:
        return self.orders.get_all()
