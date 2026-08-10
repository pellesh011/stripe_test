from dataclasses import dataclass

from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


@dataclass
class OrderItem:
    id: int | None
    product: Product
    product_price: ProductPrice

    @classmethod
    def restore(
        cls,
        *,
        id: int,
        product: Product,
        product_price: ProductPrice,
    ) -> OrderItem:
        return cls(
            id=id,
            product=product,
            product_price=product_price,
        )
