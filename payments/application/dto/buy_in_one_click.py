from dataclasses import dataclass


@dataclass(frozen=True)
class BuyInOneClickDTO:
    product_id: int
    product_price_id: int
    currency: str
    discount: str | None = None
