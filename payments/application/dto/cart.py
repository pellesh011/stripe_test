from dataclasses import dataclass


@dataclass(frozen=True)
class AddToCartDTO:
    product_id: int
    product_price_id: int
    cart_id: int | None = None
