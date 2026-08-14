from payments.domain.entities.order import Order, OrderStatus
from payments.domain.repositories.order import OrderRepository
from payments.domain.repositories.payment_attempt import PaymentAttemptRepository

PAYABLE_STATUSES = frozenset(
    {
        OrderStatus.CREATED,
        OrderStatus.PENDING_PAYMENT,
    }
)


class GetOrdersUseCase:
    def __init__(
        self,
        orders: OrderRepository,
        payment_attempts: PaymentAttemptRepository,
    ):
        self.orders = orders
        self.payment_attempts = payment_attempts

    def execute(self) -> list[Order]:
        orders = self.orders.get_all()
        for order in orders:
            if order.id is None or order.status not in PAYABLE_STATUSES:
                continue
            attempts = self.payment_attempts.get_by_order_id(order.id)
            attempt = next(
                (
                    item
                    for item in attempts
                    if item.external_id is not None and item.client_secret is not None
                ),
                None,
            )
            if attempt is None:
                continue
            order.payment_intent = attempt.external_id
            order.client_secret = attempt.client_secret
        return orders
