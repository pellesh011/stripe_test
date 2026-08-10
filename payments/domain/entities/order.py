from dataclasses import dataclass
from enum import Enum

from payments.domain.entities.cart import Cart
from payments.domain.entities.currency import Currency
from payments.domain.entities.order_item import OrderItem
from payments.domain.exceptions import ProductCurrencyError


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
    currency: Currency
    items: list[OrderItem]
    status: OrderStatus
    cart: Cart

    def __init__(self, currency: Currency, cart: Cart, id: int | None = None):
        self.currency = currency
        self.items = []
        self.status = OrderStatus.CREATED
        self.cart = cart
        self.id = id

    def add(self, item: OrderItem):
        if item.product_price.currency.currency != self.currency.currency:
            raise ProductCurrencyError()
        self.items.append(item)

    @classmethod
    def restore(
        cls,
        currency: Currency,
        cart: Cart,
        items: list[OrderItem],
        status: OrderStatus,
        id: int | None = None,
    ) -> Order:
        order = cls(currency=currency, cart=cart, id=id)

        order.items = items
        order.status = status

        return order
