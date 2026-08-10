from dataclasses import dataclass
from typing import TYPE_CHECKING

from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice

if TYPE_CHECKING:
    from payments.domain.entities.order import Order


@dataclass
class OrderItem:
    id: int | None
    product: Product
    product_price: ProductPrice
    order: Order | None

    def __init__(
        self,
        product: Product,
        product_price: ProductPrice,
        id: int | None = None,
        order: Order | None = None,
    ):
        self.product = product
        self.product_price = product_price
        self.id = id
        self.order = order

    @classmethod
    def restore(
        cls,
        *,
        id: int,
        product: Product,
        product_price: ProductPrice,
        order: Order | None = None,
    ) -> OrderItem:
        return cls(
            id=id,
            product=product,
            product_price=product_price,
            order=order,
        )
