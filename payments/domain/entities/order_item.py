from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from payments.domain.entities.exchange_rate import ExchangeRate
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice

if TYPE_CHECKING:
    from payments.domain.entities.order import Order


@dataclass
class OrderItem:
    id: int | None
    product: Product
    product_price: ProductPrice
    exchange_rate: ExchangeRate
    price: Decimal
    order: Order | None

    def __init__(
        self,
        product: Product,
        product_price: ProductPrice,
        exchange_rate: ExchangeRate,
        price: Decimal,
        id: int | None = None,
        order: Order | None = None,
    ):
        self.product = product
        self.product_price = product_price
        self.exchange_rate = exchange_rate
        self.price = price
        self.id = id
        self.order = order

    @classmethod
    def restore(
        cls,
        *,
        id: int,
        product: Product,
        product_price: ProductPrice,
        exchange_rate: ExchangeRate,
        price: Decimal,
        order: Order | None = None,
    ) -> OrderItem:
        return cls(
            id=id,
            product=product,
            product_price=product_price,
            exchange_rate=exchange_rate,
            price=price,
            order=order,
        )
