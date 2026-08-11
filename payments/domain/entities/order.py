from dataclasses import dataclass
from enum import Enum

from payments.domain.entities.cart import Cart
from payments.domain.entities.discount import Discount
from payments.domain.entities.exchange_rate import Currencies
from payments.domain.entities.order_item import OrderItem


class OrderStatus(Enum):
    CREATED = "created"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class Order:
    id: int | None
    currency: Currencies
    items: list[OrderItem]
    status: OrderStatus
    cart: Cart
    discount: Discount | None

    def __init__(
        self,
        currency: Currencies,
        cart: Cart,
        discount: Discount | None = None,
        id: int | None = None,
    ):
        self.currency = currency
        self.items = []
        self.status = OrderStatus.CREATED
        self.cart = cart
        self.discount = discount
        self.id = id

    def add(self, item: OrderItem):
        self.items.append(item)

    @classmethod
    def restore(
        cls,
        currency: Currencies,
        cart: Cart,
        items: list[OrderItem],
        status: OrderStatus,
        discount: Discount | None = None,
        id: int | None = None,
    ) -> Order:
        order = cls(currency=currency, cart=cart, discount=discount, id=id)

        order.items = items
        order.status = status

        return order
