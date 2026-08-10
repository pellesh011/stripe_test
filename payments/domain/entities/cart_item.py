from dataclasses import dataclass
from typing import TYPE_CHECKING

from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice

if TYPE_CHECKING:
    from payments.domain.entities.cart import Cart


@dataclass
class CartItem:
    id: int | None
    product: Product
    product_price: ProductPrice
    cart: Cart | None

    def __init__(
        self,
        product: Product,
        product_price: ProductPrice,
        id: int | None = None,
        cart: Cart | None = None,
    ):
        self.product = product
        self.product_price = product_price
        self.id = id
        self.cart = cart

    @classmethod
    def restore(
        cls,
        *,
        id: int,
        product: Product,
        product_price: ProductPrice,
        cart: Cart | None = None,
    ) -> CartItem:
        return cls(
            id=id,
            product=product,
            product_price=product_price,
            cart=cart,
        )
