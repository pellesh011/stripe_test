from dataclasses import dataclass
from enum import Enum

from payments.domain.entities.cart_item import CartItem
from payments.domain.exceptions import (
    CartItemNotFoundError,
    CartNotActiveError,
    IdentificatorError,
)


class CartStatus(Enum):
    ACTIVE = "active"
    CHECKOUT = "checkout"
    CONVERTED = "converted"
    ABANDONED = "abandoned"
    EXPIRED = "expired"


@dataclass
class Cart:
    id: int | None
    items: list[CartItem]
    status: CartStatus

    def __init__(self, id: int | None = None):
        self.status = CartStatus.ACTIVE
        self.items = []
        self.id = id

    def add(self, item: CartItem):
        self.items.append(item)

    def remove(self, item: CartItem):
        if self.status is not CartStatus.ACTIVE:
            raise CartNotActiveError()

        for index, current_item in enumerate(self.items):
            if item.id == current_item.id:
                del self.items[index]
                return

        raise CartItemNotFoundError()

    def get_id(self) -> int:
        if self.id is None:
            raise IdentificatorError()
        return self.id

    @classmethod
    def restore(
        cls,
        items: list[CartItem],
        status: CartStatus,
        id: int | None = None,
    ) -> Cart:
        cart = cls(id=id)

        cart.items = items
        cart.status = status

        return cart
