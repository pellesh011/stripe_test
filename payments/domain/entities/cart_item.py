from dataclasses import dataclass

from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


@dataclass
class CartItem:
    id: int | None
    product: Product
    product_price: ProductPrice

    def __init__(self, product: Product, product_price: ProductPrice, id: int|None = None):
        self.product = product
        self.product_price = product_price
        self.id = id

    @classmethod
    def restore(
        cls,
        *,
        id: int,
        product: Product,
        product_price: ProductPrice,
    ) -> "CartItem":
        return cls(
            id=id,
            product=product,
            product_price=product_price,
        )