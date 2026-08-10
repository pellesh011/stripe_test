from dataclasses import dataclass
from enum import Enum

from payments.domain.entities.cart_item import CartItem
from payments.domain.entities.currency import Currency
from payments.domain.exceptions import (
    CartItemNotFoundError,
    CartNotActiveError,
    ProductCurrencyError,
)


class CartStatus(Enum):
    ACTIVE = "active"
    CHECKOUT = "checkout"
    CONVERTED = "converted"
    ABANDONED = "abandoned"
    EXPIRED = "expired"


@dataclass
class Cart:
    currency: Currency
    items: list[CartItem]
    status: CartStatus

    def __init__(self, currency: Currency):
        self.status = CartStatus.ACTIVE
        self.currency = currency
        self.items = []

    def add(self, item: CartItem):
        if item.product_price.currency.currency != self.currency.currency:
            raise ProductCurrencyError()
        self.items.append(item)

    def remove(self, item: CartItem):
        if self.status is not CartStatus.ACTIVE:
            raise CartNotActiveError()

        for index, current_item in enumerate(self.items):
            if item.id == current_item.id:
                del self.items[index]
                return

        raise CartItemNotFoundError()

    @classmethod
    def restore(
        cls,
        currency: Currency,
        items: list[CartItem],
        status: CartStatus,
    ) -> Cart:
        cart = cls(currency)

        cart.items = items
        cart.status = status

        return cart
