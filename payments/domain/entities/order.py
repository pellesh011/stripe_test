from dataclasses import dataclass
from enum import Enum

from payments.domain.entities.cart import Cart
from payments.domain.entities.currency import Currency
from payments.domain.entities.order_item import OrderItem


class ProdoctCurrencyError(Exception):
    pass


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
    currency: Currency
    items: list[OrderItem]
    status: OrderStatus
    cart: Cart

    def __init__(self, currency: Currency, cart: Cart):
        self.currency = currency
        self.items = []
        self.status = OrderStatus.CREATED
        self.cart = cart

    def add(self, item: OrderItem):
        if item.product_price.currency != self.currency.currency:
            raise ProdoctCurrencyError()
        self.items.append(item)
